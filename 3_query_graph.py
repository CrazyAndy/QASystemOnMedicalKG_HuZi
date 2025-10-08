from utils.logger_utils import info
from utils.neo4j_utils import Neo4jUtils


graph_db_utils = Neo4jUtils()

def query_disease_and_drug_by_symptom(symptoms):
    for symptom in symptoms:
        relationships = graph_db_utils.find_node_by_relationship(from_node={"label": "Symptom", "properties": {"name": symptom}}, relationship_type="symptom_disease")  
        if relationships['success']:
            for relationship in relationships['relationships']:
                info(f"症状:{symptom} 疾病:{relationship.properties['name']}")
                
                    