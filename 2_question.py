import json
from utils.chroma_utils import ChromeUtils
from utils.llm_utils import query_llm
from utils.logger_utils import info

chroma_utils = ChromeUtils()

def extract_entity_from_question(question):
    system_prompt = """
    你是一个具有多年问诊经验的中医医生，具有丰富的中医知识，能够根据问题，提取出问题中的实体和关系。
    实体有可能是疾病Disease、症状Symptom、药品Drug。
    关系有可能是recommand_eat(推荐食谱)、recommand_drug(推荐药品)、has_symptom(症状)。"""
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
    "relationship":["has_symptom"]}}
    
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
    if data['Disease']:
       for disease in data['Disease']:             
           result = chroma_utils.query_document(disease,"entity",10)
           diseases.extend(result['documents'][0])
       info(f"向量检索得到疾病:{diseases}")
#     # 2, 查询症状
#     if data['Symptom']:
#        results = chroma_utils.query_document(data['Symptom'].join(","),len(data['Symptom']))
#        info(f"向量检索得到症状:{results}")
#     # 3, 查询药品
#     if data['Drug']:
#        results = chroma_utils.query_document(data['Drug'].join(","),len(data['Drug']))
#        info(f"向量检索得到药品:{results}")
#     # 4, 查询关系
#     if data['relationship']:
#        results = chroma_utils.query_document(data['relationship'].join(","),len(data['relationship']))
#        info(f"向量检索得到关系:{results}")
    
    return diseases


if __name__ == "__main__":
#     question = "感冒吃什么药?"
#     data = extract_entity_from_question(question)
#     info(f"提取到的实体和关系:{data}\n")
#     query_data_from_chroma(json.loads(data))
    
    data = {"Disease":["脱囊"],
    "Symptom":["咳嗽","头疼","流鼻涕"],
    "Drug":[],
    "relationship":["has_symptom"]}
    query_data_from_chroma(data)