import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json
from dataclasses import dataclass, asdict
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node, Tree

@dataclass
class ParsedFile:
    filepath: str
    relative_path: str
    size_bytes: int
    lines_count: int
    metadata: Dict[str, Any]
    parse_errors: List[str] = None

    def __post_init__(self):
        if self.parse_errors is None:
            self.parse_errors = []

@dataclass
class ProjectAST:
    project_root: str
    total_files: int
    total_lines: int
    total_size_bytes: int
    files: List[ParsedFile]
    parsing_errors: List[str] = None

    def __post_init__(self):
        if self.parsing_errors is None:
            self.parsing_errors = []

class PythonCodebaseParser:
    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        self.ignore_patterns = ignore_patterns or [
            '__pycache__', '.git', '.pytest_cache', 'node_modules', 'venv', '.venv',
            'env', '.env', 'dist', 'build', '*.egg-info', '.DS_Store', '.vscode', '.idea'
        ]

    def should_ignore_path(self, path: Path) -> bool:
        return any(pattern in str(path) for pattern in self.ignore_patterns)

    def find_python_files(self, root_dir: str) -> List[Path]:
        return sorted([
            file_path for file_path in Path(root_dir).rglob('*.py')
            if not self.should_ignore_path(file_path)
        ])

    def extract_semantic_info(self, node: Node, source_code: bytes, result: Dict[str, Any]):
        text = source_code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')

        if node.type == "import_statement":
            result['imports'].append(text.strip())
        elif node.type == "import_from_statement":
            result['imports'].append(text.strip())
        elif node.type == "function_definition":
            func_name = self.get_child_text(node, source_code, "identifier")
            result['functions'].append(func_name)
        elif node.type == "class_definition":
            class_name = self.get_child_text(node, source_code, "identifier")
            result['classes'].append(class_name)
        elif node.type == "assignment":
            var_name = self.get_child_text(node, source_code, "identifier")
            if var_name:
                result['variables'].append(var_name)
        elif node.type == "expression_statement" and " = " in text:
            parts = text.split("=", 1)
            var = parts[0].strip()
            if var.isidentifier():
                result['variables'].append(var)

        for child in node.children:
            self.extract_semantic_info(child, source_code, result)

    def get_child_text(self, node: Node, source_code: bytes, child_type: str) -> Optional[str]:
        for child in node.children:
            if child.type == child_type:
                return source_code[child.start_byte:child.end_byte].decode('utf-8', errors='ignore')
        return None

    def parse_file(self, file_path: Path, root_dir: str) -> ParsedFile:
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()

            stat = file_path.stat()
            lines_count = source_code.count(b'\n') + 1
            relative_path = str(file_path.relative_to(root_dir))

            tree = self.parser.parse(source_code)
            root_node = tree.root_node

            metadata = {
                "imports": [],
                "functions": [],
                "classes": [],
                "variables": [],
                "total_lines": lines_count,
                "size_bytes": stat.st_size
            }

            self.extract_semantic_info(root_node, source_code, metadata)

            parse_errors = []
            if root_node.has_error:
                parse_errors.append(f"Syntax error in {relative_path}")

            return ParsedFile(
                filepath=str(file_path),
                relative_path=relative_path,
                size_bytes=stat.st_size,
                lines_count=lines_count,
                metadata=metadata,
                parse_errors=parse_errors
            )

        except Exception as e:
            return ParsedFile(
                filepath=str(file_path),
                relative_path=str(file_path.relative_to(root_dir)),
                size_bytes=0,
                lines_count=0,
                metadata={},
                parse_errors=[f"Failed to parse {file_path}: {str(e)}"]
            )

    def parse_project(self, project_root: str, progress_callback: Optional[callable] = None) -> ProjectAST:
        root_path = Path(project_root)
        if not root_path.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

        python_files = self.find_python_files(project_root)
        if not python_files:
            return ProjectAST(project_root, 0, 0, 0, [], ["No Python files found in the project"])

        parsed_files = []
        total_lines = 0
        total_size = 0
        global_errors = []

        for i, file_path in enumerate(python_files):
            if progress_callback:
                progress_callback(i + 1, len(python_files), str(file_path))

            parsed_file = self.parse_file(file_path, project_root)
            parsed_files.append(parsed_file)
            total_lines += parsed_file.lines_count
            total_size += parsed_file.size_bytes
            global_errors.extend(parsed_file.parse_errors)

        return ProjectAST(
            project_root=project_root,
            total_files=len(parsed_files),
            total_lines=total_lines,
            total_size_bytes=total_size,
            files=parsed_files,
            parsing_errors=global_errors
        )

    def save_ast_to_json(self, project_ast: ProjectAST, output_file: str):
        data = asdict(project_ast)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_project_summary(self, project_ast: ProjectAST) -> Dict[str, Any]:
        return {
            'project_root': project_ast.project_root,
            'total_files': project_ast.total_files,
            'total_lines': project_ast.total_lines,
            'total_size_mb': round(project_ast.total_size_bytes / (1024 * 1024), 2),
            'successful_parses': sum(1 for f in project_ast.files if f.metadata),
            'failed_parses': len([f for f in project_ast.files if not f.metadata]),
            'parsing_errors_count': len(project_ast.parsing_errors),
            'files_with_errors': len([f for f in project_ast.files if f.parse_errors])
        }

def progress_callback(current: int, total: int, current_file: str):
    print(f"Progress: {current}/{total} ({(current/total)*100:.1f}%) - {current_file}")

def codebaseParser(SOURCE_DIR, OUTPUT_FILE=None, progress_callback=None):
    parser = PythonCodebaseParser()
    project_ast = parser.parse_project(SOURCE_DIR, progress_callback)
    summary = parser.get_project_summary(project_ast)

    print("\n" + "="*50)
    print("PARSING COMPLETE")
    print("="*50)
    print(f"Project: {summary['project_root']}")
    print(f"Total files: {summary['total_files']}")
    print(f"Successfully parsed: {summary['successful_parses']}")
    print(f"Failed to parse: {summary['failed_parses']}")
    print(f"Total lines: {summary['total_lines']:,}")
    print(f"Total size: {summary['total_size_mb']} MB")
    print(f"Parsing errors: {summary['parsing_errors_count']}")

    if OUTPUT_FILE:
        print(f"\nSaving results to: {OUTPUT_FILE}")
        parser.save_ast_to_json(project_ast, OUTPUT_FILE)
        print("Results saved successfully!")

    if project_ast.parsing_errors:
        print("\nParsing Errors:")
        for error in project_ast.parsing_errors[:10]:
            print(f"  - {error}")
        if len(project_ast.parsing_errors) > 10:
            print(f"  ... and {len(project_ast.parsing_errors) - 10} more errors")


