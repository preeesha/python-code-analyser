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
    ast_root: Optional[Dict[str, Any]] = None
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
            '__pycache__',
            '.git',
            '.pytest_cache',
            'node_modules',
            'venv',
            '.venv',
            'env',
            '.env',
            'dist',
            'build',
            '*.egg-info',
            '.DS_Store',
            '.vscode',
            '.idea'
        ]
    
    def should_ignore_path(self, path: Path) -> bool:
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def find_python_files(self, root_dir: str) -> List[Path]:
        python_files = []
        root_path = Path(root_dir)
        
        for file_path in root_path.rglob('*.py'):
            if not self.should_ignore_path(file_path):
                python_files.append(file_path)
        
        return sorted(python_files)
    
    def node_to_dict(self, node: Node, source_code: bytes) -> Dict[str, Any]:
        result = {
            'type': node.type,
            'start_point': node.start_point,
            'end_point': node.end_point,
            'start_byte': node.start_byte,
            'end_byte': node.end_byte,
            'text': node.text.decode('utf-8') if node.text else '',
            'is_named': node.is_named,
            'has_error': node.has_error,
            'children': []
        }
    
        for child in node.children:
            result['children'].append(self.node_to_dict(child, source_code))
        
        return result
    
    def parse_file(self, file_path: Path, root_dir: str) -> ParsedFile:
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
            
            stat = file_path.stat()
            lines_count = source_code.count(b'\n') + 1
            relative_path = str(file_path.relative_to(root_dir))
            
            tree = self.parser.parse(source_code)
            ast_dict = self.node_to_dict(tree.root_node, source_code)
            
            parse_errors = []
            if tree.root_node.has_error:
                parse_errors.append(f"Syntax error in {relative_path}")
            
            return ParsedFile(
                filepath=str(file_path),
                relative_path=relative_path,
                size_bytes=stat.st_size,
                lines_count=lines_count,
                ast_root=ast_dict,
                parse_errors=parse_errors
            )
            
        except Exception as e:
            return ParsedFile(
                filepath=str(file_path),
                relative_path=str(file_path.relative_to(root_dir)),
                size_bytes=0,
                lines_count=0,
                ast_root=None,
                parse_errors=[f"Failed to parse {file_path}: {str(e)}"]
            )
    
    def parse_project(self, project_root: str, progress_callback: Optional[callable] = None) -> ProjectAST:
        root_path = Path(project_root)
        if not root_path.exists():
            raise ValueError(f"Project root does not exist: {project_root}")
        
        python_files = self.find_python_files(project_root)
        
        if not python_files:
            return ProjectAST(
                project_root=project_root,
                total_files=0,
                total_lines=0,
                total_size_bytes=0,
                files=[],
                parsing_errors=["No Python files found in the project"]
            )
        
        parsed_files = []
        total_lines = 0
        total_size = 0
        global_errors = []
        
        for i, file_path in enumerate(python_files):
            if progress_callback:
                progress_callback(i + 1, len(python_files), str(file_path))
            
            try:
                parsed_file = self.parse_file(file_path, project_root)
                parsed_files.append(parsed_file)
                total_lines += parsed_file.lines_count
                total_size += parsed_file.size_bytes
                
                if parsed_file.parse_errors:
                    global_errors.extend(parsed_file.parse_errors)
                    
            except Exception as e:
                global_errors.append(f"Failed to process {file_path}: {str(e)}")
        
        return ProjectAST(
            project_root=project_root,
            total_files=len(parsed_files),
            total_lines=total_lines,
            total_size_bytes=total_size,
            files=parsed_files,
            parsing_errors=global_errors
        )
    
    def save_ast_to_json(self, project_ast: ProjectAST, output_file: str):
        ast_dict = asdict(project_ast)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ast_dict, f, indent=2, ensure_ascii=False)
    
    def get_project_summary(self, project_ast: ProjectAST) -> Dict[str, Any]:
        successful_parses = sum(1 for f in project_ast.files if f.ast_root is not None)
        failed_parses = len(project_ast.files) - successful_parses
        
        return {
            'project_root': project_ast.project_root,
            'total_files': project_ast.total_files,
            'successful_parses': successful_parses,
            'failed_parses': failed_parses,
            'total_lines': project_ast.total_lines,
            'total_size_mb': round(project_ast.total_size_bytes / (1024 * 1024), 2),
            'parsing_errors_count': len(project_ast.parsing_errors),
            'files_with_errors': len([f for f in project_ast.files if f.parse_errors])
        }

def progress_callback(current: int, total: int, current_file: str):
    percentage = (current / total) * 100
    print(f"Progress: {current}/{total} ({percentage:.1f}%) - {current_file}")

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
        print(f"\nSaving AST to: {OUTPUT_FILE}")
        parser.save_ast_to_json(project_ast, OUTPUT_FILE)
        print("AST saved successfully!")
    
    if project_ast.parsing_errors:
        print("\nParsing Errors:")
        for error in project_ast.parsing_errors[:10]: 
            print(f"  - {error}")
        if len(project_ast.parsing_errors) > 10:
            print(f"  ... and {len(project_ast.parsing_errors) - 10} more errors")
    













































































# import tree_sitter_python as tspython
# from tree_sitter import Language, Parser


# PY_LANGUAGE = Language(tspython.language())
# parser = Parser(PY_LANGUAGE)

# import os

# symbol_table = {
#     "module_path": {
#         "classes": [],
#         "functions": [],
#         "variables": [],
#         "imports": []
#     }
# }

# def find_python_files(root_dir):
#     for dirpath, _, filenames in os.walk(root_dir):
#         for f in filenames:
#             if f.endswith(".py"):
#                 yield os.path.join(dirpath, f)

# def parse_file(filepath, parser):
#     with open(filepath, "r", encoding="utf-8") as f:
#         source_code = f.read()
#     tree = parser.parse(bytes(source_code, "utf8"))
#     return tree, source_code

# SOURCE_DIR = "C:/Users/QSS/Desktop/MCP-Math-Solver/mcp-math-solver"

# file_syntax_trees = [parse_file(filepath, parser) for filepath in find_python_files(SOURCE_DIR)]

# def print_tree(node, source_code, indent=0):
#     indent_str = "  " * indent
#     node_text = source_code[node.start_byte:node.end_byte].encode("utf-8", errors="ignore")
#     type_map = {
#         "module": "Module",
#         "class_definition": "Class",
#         "function_definition": "Function",
#         "import_statement": "Import"
#     }
#     label = type_map.get(node.type, node.type.capitalize())
#     print(f"{indent_str}{label}: {node_text.strip()}")

#     for child in node.children:
#         print_tree(child, source_code, indent + 1)



# print("Parsing Python files in directory:", SOURCE_DIR)
# for tree, source_code in file_syntax_trees:
#     root_node = tree.root_node
#     print_tree(root_node, source_code)
#     print("\n" + "="*40 + "\n")
#     break































# import ast

# with open("sample/code.py", "r") as file:
#     source_file = file.read()

# tree = ast.parse(
#     source=source_file,
#     filename="sample_code"
# )


# for node in ast.walk(tree):
#     print(node)
#     #print(node.__dict__)
#     #print("children: " + str([x for x in ast.iter_child_nodes(node)]) + "\\n")