import json
from utils.chroma_utils import ChromeUtils
from utils.llm_utils import query_llm
from utils.logger_utils import info

chroma_utils = ChromeUtils()

def extract_entity_from_question(question):
    system_prompt = """
    你是一个具有多年问诊经验的西医医生，具有丰富的西医知识，能够根据问题，提取出问题中的实体和关系。
    实体有可能是疾病Disease、症状Symptom、药品Drug。
    关系有可能是recommand_drug(推荐药品)、symptom_disease(症状到疾病)。"""
    user_prompt = f"""
    问题: {question}
    请根据问题，提取出问题中的实体和关系。不能包含其他内容。
    
    返回json数据格式如下：
    {{"Disease":[],
    "Symptom":[],
    "Drug":[],
    "relationship":[]}}
    
    example:
    问题1: 咳嗽、头疼、流鼻涕是什么病?
    返回: {{"Disease":[""],
    "Symptom":["咳嗽","头疼","流鼻涕"],
    "Drug":[],
    "relationship":["symptom_disease"]}}
    
    问题2: 感冒应该吃什么药，吃感冒灵胶囊可以吗?
    返回: {{"Disease":["感冒"],
    "Symptom":[],
    "Drug":["感冒灵胶囊"],
    "relationship":["recommand_drug"]}}
    """
    return query_llm(system_prompt, user_prompt)


# def get_top_k_entities(question):
#     entities = extract_entity_from_question(question)
    
#     results = chroma_utils.query_document(entities,len(entities))
    
#     return results

def query_data_from_chroma(data):
    # 1, 查询疾病
    diseases = []
    symptoms = []
    drugs = []
    if data['Disease']:
       for disease in data['Disease']:             
           result = chroma_utils.query_document(disease,"Disease",1)
           diseases.extend(result['documents'][0])
       info(f"向量检索得到疾病:{diseases}")
       
    if data['Symptom']:
       for symptom in data['Symptom']:             
           result = chroma_utils.query_document(symptom,"Symptom",1)
           symptoms.extend(result['documents'][0])
       info(f"向量检索得到症状:{symptoms}")
       
    if data['Drug']:
       for drug in data['Drug']:             
           result = chroma_utils.query_document(drug,"Drug",1)
           drugs.extend(result['documents'][0])
       info(f"向量检索得到药品:{drugs}")
    
    return diseases,symptoms,drugs


if __name__ == "__main__":
#     question = "感冒吃什么药?"
#     data = extract_entity_from_question(question)
#     info(f"提取到的实体和关系:{data}\n")
#     query_data_from_chroma(json.loads(data))
    
    data = {"Disease":["感冒"],
    "Symptom":["咳嗽","头疼","流鼻涕"],
    "Drug":["益髓颗粒"],
    "relationship":["recommand_drug"]}
    query_data_from_chroma(data)