from files_from_dir import get_files_from_dir
import neo4j_functions

directories = ["testing/python-code-analyser"] 
file_extension = ".py"  

print("Starting the pipeline...")

print("Getting and parsingfiles from directories...")

get_files_from_dir(directories, file_extension)

print("Saving nodes and relationships to Neo4j...")

neo4j_functions.deleting_all_nodes_and_relationships()
neo4j_functions.saving_nodes_to_neo4j("output/parsed_code.json")
neo4j_functions.saving_relationships_to_neo4j("output/parsed_code.json")
neo4j_functions.close_driver()

print("Ingestion Pipeline completed.")
