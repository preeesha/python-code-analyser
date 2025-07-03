from utils import load_json_file, save_json_file

def convert_ast_to_neo4j_format(input_file, output_nodes_file, output_relationships_file):
    project_ast = load_json_file(input_file)
    nodes = []
    relationships = []
    node_ids = set()

    for file in project_ast['files']:
        file_id = f"{file['relative_path']}"
        if file_id not in node_ids:
            nodes.append({"id": file_id, "type": "File", "properties": {"path": file['relative_path']}})
            node_ids.add(file_id)

        def traverse(node, parent_id=None):
            node_type = node.get('type')
            text = node.get('text', '').strip()
            entity_id = None
            # Handle Classes
            if node_type == "class_definition":
                entity_id = f"{file['relative_path']}::{text}"
                if entity_id not in node_ids:
                    nodes.append({"id": entity_id, "type": "Class", "properties": {"name": text}})
                    node_ids.add(entity_id)
                relationships.append({
                    "source": {"id": file_id, "type": "File"},
                    "target": {"id": entity_id, "type": "Class"},
                    "type": "CONTAINS",
                    "properties": {}
                })
            # Handle Functions
            if node_type == "function_definition":
                entity_id = f"{file['relative_path']}::{text}"
                if entity_id not in node_ids:
                    nodes.append({"id": entity_id, "type": "Function", "properties": {"name": text}})
                    node_ids.add(entity_id)
                relationships.append({
                    "source": {"id": file_id, "type": "File"},
                    "target": {"id": entity_id, "type": "Function"},
                    "type": "CONTAINS",
                    "properties": {}
                })
            # Handle Imports
            if node_type == "import_statement":
                target_module = text.replace("import", "").strip()
                if target_module not in node_ids:
                    nodes.append({"id": target_module, "type": "Module", "properties": {}})
                    node_ids.add(target_module)
                relationships.append({
                    "source": {"id": file_id, "type": "File"},
                    "target": {"id": target_module, "type": "Module"},
                    "type": "IMPORTS",
                    "properties": {}
                })
            # Recursively process children
            for child in node.get('children', []):
                traverse(child, parent_id=entity_id or file_id)

        if file['ast_root']:
            traverse(file['ast_root'])

    save_json_file(nodes, output_nodes_file)
    save_json_file(relationships, output_relationships_file)

