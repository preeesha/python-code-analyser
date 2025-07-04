import os
from file_utils import ensure_clean_json_file, save_results_to_json
from display import display_graph_info, display_parsing_summary, print_header
from llm_setup import get_default_llm_and_transformer
from code_parser import parse_code_with_llm


def main():
    """
    Main function to orchestrate the code parsing workflow
    """
    print_header("Code Analysis and Graph Transformation")
    
    # Configuration
    target_file = "test7.py"
    output_json = "parsed_code.json"
    
    # Ensure clean start
    ensure_clean_json_file(output_json)
    print("🔄 Starting fresh code parsing...")
    
    # Initialize LLM and transformer
    llm, transformer = get_default_llm_and_transformer()
    if llm is None or transformer is None:
        print("❌ Failed to initialize LLM. Exiting.")
        return
    
    # Parse the code
    result = parse_code_with_llm(target_file, transformer)
    
    # Display results
    if result:
        display_parsing_summary(result)
        display_graph_info(result)
        
        # Save results to JSON file
        json_file = save_results_to_json(result, output_json)
        if json_file:
            print(f"🔗 You can view the JSON file: {json_file}")
            print(
                f"📄 File contains {len(result['nodes'])} nodes and {len(result['relationships'])} relationships"
            )
        else:
            print("❌ Failed to save results to JSON.")
    else:
        print("❌ No results to save - parsing failed.")


if __name__ == "__main__":
    main()
