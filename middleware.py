from utils import load_json_file, save_json_file
from pathlib import Path

def convert_ast_to_neo4j_format(input_file, output_nodes_file, output_relationships_file):
    project_ast = load_json_file(input_file)
    nodes = []
    relationships = []
    node_ids = set()

    # Build quick lookup for files by basename (without .py)
    file_lookup = {}
    for file in project_ast['files']:
        base = Path(file['relative_path']).stem  # e.g., parser_agent
        file_lookup[base] = file['relative_path']

    for file in project_ast['files']:
        file_id = file['relative_path']
        
        if file_id not in node_ids:
            nodes.append({
                "id": file_id,
                "type": "File",
                "properties": {
                    "path": file['relative_path'],
                    "size_bytes": file.get('size_bytes', 0),
                    "lines_count": file.get('lines_count', 0)
                }
            })
            node_ids.add(file_id)

        metadata = file.get("metadata", {})

        # Handle Imports - Only create IMPORTS relationship for known project files
        for imp in metadata.get("imports", []):
            imp_clean = imp.replace("import", "").replace("from", "").split()[0].strip()
            
            if imp_clean in file_lookup:
                target_file = file_lookup[imp_clean]
                
                if target_file not in node_ids:
                    nodes.append({"id": target_file, "type": "File", "properties": {"path": target_file}})
                    node_ids.add(target_file)

                relationships.append({
                    "source": {"id": file_id, "type": "File"},
                    "target": {"id": target_file, "type": "File"},
                    "type": "IMPORTS",
                    "properties": {}
                })

        # Handle Classes
        for cls in metadata.get("classes", []):
            class_id = f"{file_id}::{cls}"
            if class_id not in node_ids:
                nodes.append({"id": class_id, "type": "Class", "properties": {"name": cls}})
                node_ids.add(class_id)
            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": class_id, "type": "Class"},
                "type": "CONTAINS",
                "properties": {}
            })

        # Handle Functions
        for func in metadata.get("functions", []):
            func_id = f"{file_id}::{func}"
            if func_id not in node_ids:
                nodes.append({"id": func_id, "type": "Function", "properties": {"name": func}})
                node_ids.add(func_id)
            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": func_id, "type": "Function"},
                "type": "CONTAINS",
                "properties": {}
            })

        # Handle Variables
        for var in metadata.get("variables", []):
            var_id = f"{file_id}::{var}"
            if var_id not in node_ids:
                nodes.append({"id": var_id, "type": "Variable", "properties": {"name": var}})
                node_ids.add(var_id)
            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": var_id, "type": "Variable"},
                "type": "CONTAINS",
                "properties": {}
            })

    save_json_file(nodes, output_nodes_file)
    save_json_file(relationships, output_relationships_file)

