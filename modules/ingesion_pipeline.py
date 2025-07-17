from modules.utils.files_from_dir import get_files_from_dir
import modules.utils.neo4j_functions as neo4j_functions
from modules.utils.file_utils import clear_directory
from modules.config.custom_logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)


def ingestion_pipeline(directories: list[str], file_extension: str):
    directories = directories
    file_extension = f".{file_extension}"

    logger.info("Starting the pipeline...")

    logger.info("Getting and parsing files from directories...")

    get_files_from_dir(directories, file_extension)

    logger.info("Saving nodes and relationships to Neo4j...")

    neo4j_functions.deleting_all_nodes_and_relationships()
    neo4j_functions.saving_nodes_to_neo4j("outputs/parsed_code.json")
    neo4j_functions.saving_relationships_to_neo4j("outputs/parsed_code.json")
    neo4j_functions.close_driver()

    logger.success("Ingestion Pipeline completed.")

    # Clear testing directory after successful ingestion
    clear_directory("testing")
