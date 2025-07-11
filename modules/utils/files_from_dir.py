import os
from modules.llm.llm_setup import get_default_llm_and_transformer
from modules.utils.code_parser import parse_code_with_llm
from modules.utils.file_utils import save_results_to_json
from modules.utils.file_utils import delete_file_content

os.makedirs("outputs", exist_ok=True)

delete_file_content(os.path.join("outputs", "parsed_code.json"))

llm, transformer = get_default_llm_and_transformer()

def check_llm():
    global llm, transformer
    if llm is None or transformer is None:
        print("❌ Failed to initialize LLM. Exiting.")
        exit()
    else:
        print("✅ LLM initialized successfully.")

def get_files_from_dir(directories, file_extension=".py"):
    global llm, transformer
    check_llm()
    
    for dir_name in directories:
        for root, dirs, files in os.walk(dir_name):
            for file in files:
                if file.endswith(file_extension):
                    file_path = os.path.join(root, file)
                    try:
                        result = parse_code_with_llm(file_path, transformer)
                        if result:
                            json_file = save_results_to_json(result)
                            if json_file:
                                print(f"🔗 You can view the JSON file: {json_file}")
                                print(
                                    f"📄 File contains {len(result['nodes'])} nodes and {len(result['relationships'])} relationships"
                                )
                            else:
                                print("❌ Failed to save results to JSON.")
                        else:
                            print(f"⚠️ Parsing produced no nodes for {file_path}. Skipping.")
                    except Exception as e:
                        print(f"❌ Failed to read {file_path}: {e}")
                else:
                    print("❌ No results to save - parsing failed.")



