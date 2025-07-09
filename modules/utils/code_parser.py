import hashlib
from datetime import datetime
from langchain_core.documents import Document

from modules.config.config import MAX_CHUNK_SIZE, LARGE_FILE_THRESHOLD, CHUNK_OVERLAP_LINES


def split_code_into_chunks(code_content, max_chunk_size=MAX_CHUNK_SIZE):
    if len(code_content) <= max_chunk_size:
        return [code_content]
    
    lines = code_content.split("\n")
    chunks, current_chunk, current_size = [], [], 0
    
    for line in lines:
        line_size = len(line) + 1
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            overlap = current_chunk[-CHUNK_OVERLAP_LINES:] if len(current_chunk) > CHUNK_OVERLAP_LINES else current_chunk
            current_chunk = overlap + [line]
            current_size = sum(len(l) + 1 for l in current_chunk)
        else:
            current_chunk.append(line)
            current_size += line_size

    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks


def read_and_analyze_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None


def process_single_chunk(chunk, metadata, transformer):
    try:
        docs = [Document(page_content=chunk, metadata=metadata)]
        graph_docs = transformer.convert_to_graph_documents(docs)
        if graph_docs and graph_docs[0]:
            return graph_docs[0].nodes, graph_docs[0].relationships
    except Exception as e:
        print(f"❌ Chunk processing error: {e}")
    return [], []


def parse_large_file_in_chunks(code_content, transformer):
    chunks = split_code_into_chunks(code_content)
    current_time = datetime.now().isoformat()
    
    all_nodes, all_relationships = [], []

    for i, chunk in enumerate(chunks):
        unique_id = hashlib.md5(f"{chunk}{current_time}".encode()).hexdigest()[:16]
        metadata = {"source": f"chunk_{i+1}", "unique_id": unique_id}
        nodes, relationships = process_single_chunk(chunk, metadata, transformer)
        all_nodes.extend(nodes)
        all_relationships.extend(relationships)

    unique_nodes = {getattr(n, "id", str(n)): n for n in all_nodes}

    return {
        "nodes": list(unique_nodes.values()),
        "relationships": all_relationships,
        "node_count": len(unique_nodes),
        "relationship_count": len(all_relationships),
        "chunks_processed": len(chunks),
    }


def parse_small_file(code_content, transformer):
    unique_id = hashlib.md5(code_content.encode()).hexdigest()[:16]
    metadata = {"source": "single_file", "unique_id": unique_id}
    nodes, relationships = process_single_chunk(code_content, metadata, transformer)

    if nodes or relationships:
        return {
            "nodes": nodes,
            "relationships": relationships,
            "node_count": len(nodes),
            "relationship_count": len(relationships),
            "chunks_processed": 1,
        }
    else:
        return None


def parse_code_with_llm(file_path, transformer):
    code_content = read_and_analyze_file(file_path)
    if not code_content:
        return None

    if len(code_content) > LARGE_FILE_THRESHOLD:
        result = parse_large_file_in_chunks(code_content, transformer)
    else:
        result = parse_small_file(code_content, transformer)

    if result:
        result["file"] = file_path
    return result
