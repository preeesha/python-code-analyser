from modules.utils.files_from_dir import get_files_from_dir
import modules.utils.neo4j_functions as neo4j_functions
from modules.utils.file_utils import clear_directory


def ingestion_pipeline(directories: list[str], file_extension: str):
    directories = directories
    file_extension = f".{file_extension}"

    print("Starting the pipeline...")

    print("Getting and parsingfiles from directories...")

    get_files_from_dir(directories, file_extension)

    print("Saving nodes and relationships to Neo4j...")

    neo4j_functions.deleting_all_nodes_and_relationships()
    neo4j_functions.saving_nodes_to_neo4j("outputs/parsed_code.json")
    neo4j_functions.saving_relationships_to_neo4j("outputs/parsed_code.json")
    neo4j_functions.close_driver()

    print("Ingestion Pipeline completed.")

    # Clear testing directory after successful ingestion
    clear_directory("testing")
