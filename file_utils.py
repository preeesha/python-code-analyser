"""
File utilities module for saving and loading results
"""

import json
import os
from datetime import datetime


def save_results_to_json(graph_info, output_file=None):
    """
    Save the parsed graph information to a JSON file.

    Args:
        graph_info (dict): Graph information from parse_code_with_llm
        output_file (str): Output file path (optional)

    Returns:
        str: Path to the saved JSON file
    """
    if not graph_info:
        print("No graph information to save.")
        return None

    # Generate output filename if not provided
    if not output_file:
        output_file = "parsed_code.json"

    # Convert complex objects to serializable format
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

    # Convert nodes to dictionaries
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

    # Convert relationships to dictionaries
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

    # Save to JSON file
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