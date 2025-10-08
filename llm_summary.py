from utils.llm_utils import query_llm
from utils.logger_utils import info



def llm_summary(question, diseases,disease_names, drugs):
    system_prompt = """
    你是一个具有多年问诊经验的西医医生，具有丰富的中医知识。
    你能够根据问题，以及我提供的可能性疾病，需要治疗的药物，来给患者一个完整的诊断。
    你给出的诊断需要包含疾病名称，疾病描述，疾病治疗方案，疾病治疗药物。
    """
    user_prompt = f"""
    用户问题: {question}
    可能患的疾病: {disease_names}
    可能患的疾病详情: {diseases}
    可能需要的药品: {drugs}
    """
    return query_llm(system_prompt, user_prompt)

if __name__ == "__main__":
    question = "我最近头痛，流鼻涕，咳嗽，应该吃什么药?"
    diseases = ["感冒"]
    drugs = ["感冒灵胶囊"]
    result = llm_summary(question, diseases, drugs)
    info(f"总结结果: {result}")