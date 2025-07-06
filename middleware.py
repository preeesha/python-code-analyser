from utils import load_json_file, save_json_file
from pathlib import Path

def convert_ast_to_neo4j_format(input_file, output_nodes_file, output_relationships_file):
    project_ast = load_json_file(input_file)
    nodes = []
    relationships = []
    node_ids = set()

    # Create a lookup for file imports - map module names to file paths
    file_lookup = {Path(file['relative_path']).stem: file['relative_path'] for file in project_ast['files']}

    for file in project_ast['files']:
        file_id = file['relative_path']

        # Add file node
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

        # Handle Imports
        for imp in metadata.get("imports", []):
            # Clean up import statement to extract module name
            imp_clean = imp.replace("import", "").replace("from", "").split()[0].strip()
            if imp_clean in file_lookup:
                target_file = file_lookup[imp_clean]

                if target_file not in node_ids:
                    nodes.append({
                        "id": target_file,
                        "type": "File",
                        "properties": {"path": target_file}
                    })
                    node_ids.add(target_file)

                relationships.append({
                    "source": {"id": file_id, "type": "File"},
                    "target": {"id": target_file, "type": "File"},
                    "type": "IMPORTS",
                    "properties": {"import_statement": imp.strip()}
                })

        # Handle Classes (dictionary structure with full_name as key)
        for class_full_name, cls in metadata.get("classes", {}).items():
            class_name = cls["name"]
            class_id = f"{file_id}::{class_name}"

            if class_id not in node_ids:
                nodes.append({
                    "id": class_id,
                    "type": "Class",
                    "properties": {
                        "name": class_name,
                        "full_name": cls.get("full_name", class_name)
                    }
                })
                node_ids.add(class_id)

            # File contains class relationship
            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": class_id, "type": "Class"},
                "type": "CONTAINS",
                "properties": {}
            })

            # Handle Class Methods (dictionary structure with full_name as key)
            for method_full_name, method in cls.get("methods", {}).items():
                method_name = method["name"]
                method_id = f"{class_id}::{method_name}"

                if method_id not in node_ids:
                    nodes.append({
                        "id": method_id,
                        "type": "Function",
                        "properties": {
                            "name": method_name,
                            "full_name": method.get("full_name", method_name),
                            "parameters": method.get("parameters", []),
                            "is_method": True
                        }
                    })
                    node_ids.add(method_id)

                # Class contains method relationship
                relationships.append({
                    "source": {"id": class_id, "type": "Class"},
                    "target": {"id": method_id, "type": "Function"},
                    "type": "CONTAINS",
                    "properties": {}
                })

                # Handle variables inside method
                for var_full_name in method.get("variables", []):
                    var_name = var_full_name.split('.')[-1]
                    var_id = f"{method_id}::{var_name}"
                    
                    if var_id not in node_ids:
                        nodes.append({
                            "id": var_id,
                            "type": "Variable",
                            "properties": {
                                "name": var_name,
                                "full_name": var_full_name,
                                "scope": "method"
                            }
                        })
                        node_ids.add(var_id)

                    relationships.append({
                        "source": {"id": method_id, "type": "Function"},
                        "target": {"id": var_id, "type": "Variable"},
                        "type": "CONTAINS",
                        "properties": {}
                    })

            # Handle Class Attributes
            for attr_full_name in cls.get("attributes", []):
                attr_name = attr_full_name.split('.')[-1]
                attr_id = f"{class_id}::{attr_name}"

                if attr_id not in node_ids:
                    nodes.append({
                        "id": attr_id,
                        "type": "Variable",
                        "properties": {
                            "name": attr_name,
                            "full_name": attr_full_name,
                            "scope": "class"
                        }
                    })
                    node_ids.add(attr_id)

                relationships.append({
                    "source": {"id": class_id, "type": "Class"},
                    "target": {"id": attr_id, "type": "Variable"},
                    "type": "CONTAINS",
                    "properties": {}
                })

        # Handle File-level Functions (dictionary structure with full_name as key)
        for func_full_name, func in metadata.get("functions", {}).items():
            func_name = func["name"]
            func_id = f"{file_id}::{func_name}"

            if func_id not in node_ids:
                nodes.append({
                    "id": func_id,
                    "type": "Function",
                    "properties": {
                        "name": func_name,
                        "full_name": func.get("full_name", func_name),
                        "parameters": func.get("parameters", []),
                        "is_method": False
                    }
                })
                node_ids.add(func_id)

            # File contains function relationship
            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": func_id, "type": "Function"},
                "type": "CONTAINS",
                "properties": {}
            })

            # Handle variables inside function
            for var_full_name in func.get("variables", []):
                var_name = var_full_name.split('.')[-1]
                var_id = f"{func_id}::{var_name}"

                if var_id not in node_ids:
                    nodes.append({
                        "id": var_id,
                        "type": "Variable",
                        "properties": {
                            "name": var_name,
                            "full_name": var_full_name,
                            "scope": "function"
                        }
                    })
                    node_ids.add(var_id)

                relationships.append({
                    "source": {"id": func_id, "type": "Function"},
                    "target": {"id": var_id, "type": "Variable"},
                    "type": "CONTAINS",
                    "properties": {}
                })

        # Handle File-level Variables
        for var_full_name in metadata.get("variables", []):
            var_name = var_full_name.split('.')[-1] if '.' in var_full_name else var_full_name
            var_id = f"{file_id}::{var_name}"

            if var_id not in node_ids:
                nodes.append({
                    "id": var_id,
                    "type": "Variable",
                    "properties": {
                        "name": var_name,
                        "full_name": var_full_name,
                        "scope": "module"
                    }
                })
                node_ids.add(var_id)

            relationships.append({
                "source": {"id": file_id, "type": "File"},
                "target": {"id": var_id, "type": "Variable"},
                "type": "CONTAINS",
                "properties": {}
            })

    # Save results
    save_json_file(nodes, output_nodes_file)
    save_json_file(relationships, output_relationships_file)
    
    print(f"Generated {len(nodes)} nodes and {len(relationships)} relationships")
    print(f"Nodes saved to: {output_nodes_file}")
    print(f"Relationships saved to: {output_relationships_file}")
