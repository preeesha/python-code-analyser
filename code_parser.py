"""
Code parsing and graph transformation module
"""

import hashlib
import re
from datetime import datetime
from langchain_core.documents import Document

from config import MAX_CHUNK_SIZE, LARGE_FILE_THRESHOLD, CHUNK_OVERLAP_LINES


def split_code_into_chunks(code_content, max_chunk_size=MAX_CHUNK_SIZE):
    """
    Split large code files into smaller chunks for better LLM processing
    
    Args:
        code_content (str): The complete code content
        max_chunk_size (int): Maximum size per chunk
        
    Returns:
        list: List of code chunks with overlap for context
    """
    if len(code_content) <= max_chunk_size:
        return [code_content]
    
    lines = code_content.split("\n")
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        if current_size + line_size > max_chunk_size and current_chunk:
            # Save current chunk
            chunks.append("\n".join(current_chunk))
            
            # Start new chunk with some overlap (last N lines for context)
            overlap_lines = (
                current_chunk[-CHUNK_OVERLAP_LINES:] 
                if len(current_chunk) > CHUNK_OVERLAP_LINES 
                else current_chunk
            )
            current_chunk = overlap_lines + [line]
            current_size = sum(len(l) + 1 for l in current_chunk)
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Add final chunk
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks


def read_and_analyze_file(file_path):
    """
    Read file and extract basic information
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        dict: File information including content, hash, and function count
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code_content = file.read()
            
        # Generate content hash for debugging
        content_hash = hashlib.md5(code_content.encode()).hexdigest()[:8]
        
        # Count functions for verification
        func_matches = re.findall(r"^def\s+(\w+)", code_content, re.MULTILINE)
        
        file_info = {
            "content": code_content,
            "hash": content_hash,
            "size": len(code_content),
            "functions": func_matches,
            "function_count": len(func_matches)
        }
        
        print(f"📁 Reading file: {file_path}")
        print(f"🔍 Content hash: {content_hash}")
        print(f"📏 File size: {len(code_content)} characters")
        print(f"🔍 Functions found in file: {len(func_matches)}")
        print(f"🔍 Function names: {func_matches[:10]}...")  # Show first 10
        
        # Show file content preview
        print("📄 File content START (first 300 chars):")
        print(code_content[:300])
        print("\n📄 File content END (last 300 chars):")
        print(code_content[-300:])
        
        return file_info
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def process_single_chunk(chunk, chunk_info, transformer):
    """
    Process a single chunk of code with the transformer
    
    Args:
        chunk (str): Code chunk to process
        chunk_info (dict): Metadata about the chunk
        transformer: LLMGraphTransformer instance
        
    Returns:
        tuple: (nodes, relationships) or ([], []) if processing fails
    """
    docs = [
        Document(
            page_content=chunk,
            metadata=chunk_info,
        )
    ]

    try:
        graph_docs = transformer.convert_to_graph_documents(docs)
        if graph_docs and graph_docs[0]:
            graph = graph_docs[0]
            return graph.nodes, graph.relationships
        else:
            return [], []
    except Exception as e:
        print(f"❌ Chunk processing error: {e}")
        return [], []


def parse_large_file_in_chunks(file_info, transformer):
    """
    Parse a large file by splitting it into chunks
    
    Args:
        file_info (dict): File information from read_and_analyze_file
        transformer: LLMGraphTransformer instance
        
    Returns:
        dict: Parsing results with nodes and relationships
    """
    code_content = file_info["content"]
    content_hash = file_info["hash"]
    current_time = datetime.now().isoformat()
    
    print(f"🔄 File is large ({len(code_content)} chars), splitting into chunks...")
    chunks = split_code_into_chunks(code_content, max_chunk_size=MAX_CHUNK_SIZE)
    print(f"📊 Split into {len(chunks)} chunks")
    
    all_nodes = []
    all_relationships = []
    
    for i, chunk in enumerate(chunks):
        print(f"🔄 Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        
        # Create unique identifier for this chunk
        unique_id = hashlib.md5(
            f"{content_hash}chunk{i}{current_time}".encode()
        ).hexdigest()[:16]
        
        chunk_info = {
            "source": f"chunk_{i+1}",
            "type": "python_code", 
            "content_hash": f"{content_hash}_chunk_{i}",
            "timestamp": current_time,
            "unique_id": unique_id,
            "file_size": len(chunk),
            "chunk_number": i + 1,
            "total_chunks": len(chunks),
        }
        
        nodes, relationships = process_single_chunk(chunk, chunk_info, transformer)
        
        if nodes or relationships:
            all_nodes.extend(nodes)
            all_relationships.extend(relationships)
            print(f"✅ Chunk {i+1}: {len(nodes)} nodes, {len(relationships)} relationships")
        else:
            print(f"⚠️ Chunk {i+1}: No results")
    
    # Deduplicate nodes by ID
    unique_nodes = {}
    for node in all_nodes:
        node_id = getattr(node, "id", str(node))
        if node_id not in unique_nodes:
            unique_nodes[node_id] = node
    
    result = {
        "nodes": list(unique_nodes.values()),
        "relationships": all_relationships,
        "node_count": len(unique_nodes),
        "relationship_count": len(all_relationships),
        "parsing_method": f"Chunked processing - {len(chunks)} chunks",
        "chunks_processed": len(chunks),
    }
    
    print(f"✅ Combined results: {len(unique_nodes)} unique nodes, {len(all_relationships)} relationships")
    return result


def parse_small_file(file_info, transformer):
    """
    Parse a small file as a single unit
    
    Args:
        file_info (dict): File information from read_and_analyze_file
        transformer: LLMGraphTransformer instance
        
    Returns:
        dict: Parsing results with nodes and relationships
    """
    code_content = file_info["content"]
    content_hash = file_info["hash"]
    current_time = datetime.now().isoformat()
    
    # Create unique identifier
    unique_id = hashlib.md5(
        f"{content_hash}{current_time}".encode()
    ).hexdigest()[:16]
    
    file_metadata = {
        "source": "single_file", 
        "type": "python_code", 
        "content_hash": content_hash,
        "timestamp": current_time,
        "unique_id": unique_id,
        "file_size": len(code_content),
    }

    print("🔄 Processing with LLM...")
    print(f"🔍 Sending {len(code_content)} characters to LLM")
    
    nodes, relationships = process_single_chunk(code_content, file_metadata, transformer)

    if nodes or relationships:
        result = {
            "nodes": nodes,
            "relationships": relationships,
            "node_count": len(nodes),
            "relationship_count": len(relationships),
            "parsing_method": "Single file processing",
            "chunks_processed": 1,
        }
        
        print(f"✅ Successfully parsed: {len(nodes)} nodes, {len(relationships)} relationships")
        return result
    else:
        print("No graph documents generated.")
        return None


def parse_code_with_llm(file_path, transformer):
    """
    Parse Python code from a file using LLMGraphTransformer
    
    Args:
        file_path (str): Path to the Python file to parse
        transformer: LLMGraphTransformer instance
        
    Returns:
        dict: Parsed graph information with nodes and relationships
    """
    # Read and analyze the file
    file_info = read_and_analyze_file(file_path)
    if file_info is None:
        return None
    
    # Add file path to result metadata
    base_result = {
        "file": file_path,
        "content_hash": file_info["hash"],
        "unique_id": f"file_{file_info['hash']}",
    }
    
    # Choose processing method based on file size
    if len(file_info["content"]) > LARGE_FILE_THRESHOLD:
        result = parse_large_file_in_chunks(file_info, transformer)
    else:
        result = parse_small_file(file_info, transformer)
    
    if result:
        # Merge base metadata with parsing results
        result.update(base_result)
        
        # Debug: Show what nodes were actually created
        print("🔍 Parsed nodes preview:")
        nodes = result.get("nodes", [])
        for i, node in enumerate(nodes[:10]):  # Show first 10 nodes
            node_name = getattr(node, "properties", {}).get(
                "name", getattr(node, "id", "unknown")
            )
            print(f"  Node {i+1}: {node.type} - {node_name}")
        
        return result
    else:
        return None 