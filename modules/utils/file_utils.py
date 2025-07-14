import json
import os
from datetime import datetime
import shutil
from pathlib import Path


def save_results_to_json(graph_info, output_file=None):
    if not graph_info:
        print("No graph information to save.")
        return None

    if not output_file:
        output_file = os.path.join("outputs", "parsed_code.json")

  
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    existing_data = None
    if output_file and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Could not read existing JSON file {output_file}: {e}")

    serializable_data = {
        "file": graph_info["file"],
        "content_hash": graph_info.get("content_hash", "unknown"),
        "unique_id": graph_info.get("unique_id", "unknown"),
        "parsing_method": graph_info.get("parsing_method", "Unknown"),
        "chunks_processed": graph_info.get("chunks_processed", 1),
        "timestamp": datetime.now().isoformat(),
        "node_count": graph_info.get("node_count", 0),
        "relationship_count": graph_info.get("relationship_count", 0),
        "nodes": [],
        "relationships": [],
    }

    if "nodes" in graph_info:
        for node in graph_info["nodes"]:
            serializable_data["nodes"].append(
                {
                    "id": str(node.id) if hasattr(node, "id") else str(node),
                    "type": str(node.type) if hasattr(node, "type") else "unknown",
                    "properties": (
                        dict(node.properties) if hasattr(node, "properties") else {}
                    ),
                }
            )

    if "relationships" in graph_info:
        for rel in graph_info["relationships"]:
            serializable_data["relationships"].append(
                {
                    "source": {
                        "id": (
                            str(rel.source.id)
                            if hasattr(rel.source, "id")
                            else str(rel.source)
                        ),
                        "type": (
                            str(rel.source.type)
                            if hasattr(rel.source, "type")
                            else "unknown"
                        ),
                    },
                    "target": {
                        "id": (
                            str(rel.target.id)
                            if hasattr(rel.target, "id")
                            else str(rel.target)
                        ),
                        "type": (
                            str(rel.target.type)
                            if hasattr(rel.target, "type")
                            else "unknown"
                        ),
                    },
                    "relationship_type": (
                        str(rel.type) if hasattr(rel, "type") else "unknown"
                    ),
                    "properties": (
                        dict(rel.properties) if hasattr(rel, "properties") else {}
                    ),
                }
            )

    if existing_data:
        existing_nodes_dict = {
            str(n.get("id")): n for n in existing_data.get("nodes", [])
        }
        for node in serializable_data["nodes"]:
            existing_nodes_dict[str(node.get("id"))] = node

        merged_nodes = list(existing_nodes_dict.values())

        def _rel_key(rel):
            return (
                rel["source"]["id"],
                rel["target"]["id"],
                rel["relationship_type"],
            )

        existing_rels_dict = {
            _rel_key(rel): rel for rel in existing_data.get("relationships", [])
        }

        for rel in serializable_data["relationships"]:
            existing_rels_dict[_rel_key(rel)] = rel

        merged_relationships = list(existing_rels_dict.values())

        serializable_data = existing_data  # start from previous metadata
        serializable_data["nodes"] = merged_nodes
        serializable_data["relationships"] = merged_relationships
        serializable_data["node_count"] = len(merged_nodes)
        serializable_data["relationship_count"] = len(merged_relationships)

        
        processed_files = set(serializable_data.get("processed_files", []))
        processed_files.add(graph_info["file"])
        serializable_data["processed_files"] = sorted(processed_files)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Results saved to: {output_file}")
        print(
            f"📊 Saved {len(serializable_data['nodes'])} nodes and {len(serializable_data['relationships'])} relationships"
        )

        return output_file

    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return None


def load_json_data(file_path):
    """
    Load data from JSON file
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        dict: Loaded data or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"JSON file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None


def ensure_clean_json_file(file_path):
    """
    Ensure clean start by removing old JSON file
    
    Args:
        file_path (str): Path to JSON file to clean
    """
    # Make sure the directory for the JSON file exists first
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"🗑️ Removed old {file_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not remove old {file_path}: {e}")


def get_file_info(file_path):
    """
    Get basic information about a file
    
    Args:
        file_path (str): Path to file
        
    Returns:
        dict: File information or None if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = os.path.getmtime(file_path)
            return {
                "path": file_path,
                "size": size,
                "modified": modified,
                "exists": True
            }
        else:
            return {
                "path": file_path,
                "exists": False
            }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None 
    
def clear_directory(path:str):
    """
    Clear all contents of the testing directory after ingestion is complete.
    """
    try:
        # Get the project root directory (two levels up from this file)
        project_root = Path(__file__).resolve().parent.parent
        testing_dir = project_root / path
        
        if testing_dir.exists():
            print("Clearing testing directory...")
            # Remove all contents of the testing directory
            for item in testing_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            print("✅ Testing directory cleared successfully")
        else:
            print("⚠️ Testing directory does not exist")
            
    except Exception as e:
        print(f"❌ Error clearing testing directory: {e}")

def delete_file_content(file_path):
    if os.path.exists(file_path) and file_path.endswith(".json"):
        try:
            with open(file_path, "w") as f:
                f.write("")
        except Exception as e:
            print(f"⚠️ Warning: Could not clear content of {file_path}: {e}")