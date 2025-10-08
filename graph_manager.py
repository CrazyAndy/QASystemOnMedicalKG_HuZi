from utils.logger_utils import info
from utils.neo4j_utils import Neo4jUtils
from collections import defaultdict


graph_db_utils = Neo4jUtils()


def query_disease_by_symptom(symptoms):
    """
    根据症状查询疾病 - 使用defaultdict消除特殊情况
    """
    diseases_info = defaultdict(lambda: {"count": 0, "properties": {}})
    
    for symptom in symptoms:
        relationships = graph_db_utils.find_node_by_relationship(
            relationship_type="symptom_disease", front_node_name=symptom)
        if relationships['success']:
            for node in relationships['nodes']:
                disease_name = node.properties['name']
                diseases_info[disease_name]["count"] += 1
                diseases_info[disease_name]["properties"] = node.properties
                # info(f"症状:{symptom} 疾病:{disease_name}")
    
    # 根据count值从大到小排序，返回前3个疾病名称
    sorted_diseases = sorted(diseases_info.items(), key=lambda x: x[1]["count"], reverse=True)
    return sorted_diseases,[disease[0] for disease in sorted_diseases[:3]]
      
def query_drug_by_disease(diseases):
    """
    根据疾病查询药品 - 使用defaultdict消除特殊情况
    """
    drugs_info = defaultdict(lambda: {"count": 0, "properties": {}})
    
    for disease in diseases:
        relationships = graph_db_utils.find_node_by_relationship(
            relationship_type="recommand_drug", front_node_name=disease)
        if relationships['success']:
            for node in relationships['nodes']:
                drug_name = node.properties['name']
                drugs_info[drug_name]["count"] += 1
                drugs_info[drug_name]["properties"] = node.properties
                # info(f"疾病:{disease} 药品:{drug_name}")
    
    # 根据count值从大到小排序，返回前3个药品名称
    sorted_drugs = sorted(drugs_info.items(), key=lambda x: x[1]["count"], reverse=True)
    return [drug[0] for drug in sorted_drugs[:3]]

if __name__ == "__main__":
    diseases,disease_names = query_disease_by_symptom(["流鼻涕","咽痛","头痛"])
#     info(f"疾病: {diseases}")
    info(f"疾病名称: {disease_names}")
    drug_names = query_drug_by_disease(disease_names)
    info(f"药品名称: {drug_names}")
    
    
    
    
