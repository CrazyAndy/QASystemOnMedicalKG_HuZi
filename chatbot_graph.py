import json
import sys
import time
from graph_manager import query_disease_by_symptom,query_drug_by_disease
from llm_summary import llm_summary
from question_parser import extract_entity_from_question,query_data_from_chroma
from utils.logger_utils import info


'''问答类'''
class ChatBotGraph:
    def __init__(self):
        pass

    def chat_main(self, question):
        print("华佗: 正在分析您的问题...", end='', flush=True)
        time.sleep(0.5)
        print(" ✓")
        
        data = extract_entity_from_question(question)
        
        print("华佗: 正在提取关键信息...", end='', flush=True)
        time.sleep(0.5)
        print(" ✓")
        
        diseases_from_chroma,symptoms_from_chroma,drugs_from_chroma = query_data_from_chroma(json.loads(data))
        
        print("华佗: 正在查询相关疾病...", end='', flush=True)
        time.sleep(0.5)
        print(" ✓")
        
        diseases,disease_names = query_disease_by_symptom(symptoms_from_chroma)
        
        info(f"诊断疾病名称: {disease_names}")
        
        print("华佗: 正在推荐治疗方案...", end='', flush=True)
        time.sleep(0.5)
        print(" ✓")
        
        drug_names = query_drug_by_disease(disease_names)
        
        info(f"推荐药品名称: {drug_names}")
        
        print("华佗: 正在生成诊断建议...", end='', flush=True)
        time.sleep(0.5)
        print(" ✓")
        
        summary = llm_summary(question, disease_names, drug_names)
        
        info(f"总结结果: {summary}")
        
        final_answers = [summary]
        if not final_answers:
            return '您好，我是华佗，希望可以帮到您。'
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    print("=" * 50)
    print("欢迎使用华佗医疗问答系统！")
    print("我是华佗，希望可以帮到您。")
    print("输入 'exit' 退出系统")
    print("=" * 50)
    
    handler = ChatBotGraph()
    while True:
        question = input('\n用户: ')
        if question.lower() == 'exit':
            print("华佗: 再见！祝您身体健康！")
            break
        answer = handler.chat_main(question)
        print(f'\n华佗: {answer}')

