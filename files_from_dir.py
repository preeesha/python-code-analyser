import os


directories = ["code"] 
file_extension = ".py"  

def get_files_from_dir(directories, file_extension=".py", combined_output_file="combined_output.py"):
    
    with open(combined_output_file, "w", encoding="utf-8") as out_f:

        for dir_name in directories:
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    if file.endswith(file_extension):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as in_f:
                                content = in_f.read()
                                out_f.write(f"# --- Start of {file_path} ---\n")
                                out_f.write(content + "\n")
                                out_f.write(f"# --- End of {file_path} ---\n\n")
                                print(f"✅ Added: {file_path}")
                        except Exception as e:
                            print(f"❌ Failed to read {file_path}: {e}")

get_files_from_dir(["code"], ".py", "combined_output.py")