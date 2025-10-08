
import os
from tqdm import tqdm
import json


cur_dir = os.getcwd() + '/dict'

# 　特征词txt文件路径
disease_path = os.path.join(cur_dir, 'disease.txt')
department_path = os.path.join(cur_dir, 'department.txt')
check_path = os.path.join(cur_dir, 'check.txt')
drug_path = os.path.join(cur_dir, 'drug.txt')
food_path = os.path.join(cur_dir, 'food.txt')
producer_path = os.path.join(cur_dir, 'producer.txt')
symptom_path = os.path.join(cur_dir, 'symptom.txt')
deny_path = os.path.join(cur_dir, 'deny.txt')


# 加载特征词
disease_wds = [i.strip()
               for i in open(disease_path, encoding="utf-8") if i.strip()]
department_wds = [i.strip() for i in open(
    department_path, encoding="utf-8") if i.strip()]
check_wds = [i.strip()
             for i in open(check_path, encoding="utf-8") if i.strip()]
drug_wds = [i.strip() for i in open(drug_path, encoding="utf-8") if i.strip()]
food_wds = [i.strip() for i in open(food_path, encoding="utf-8") if i.strip()]
producer_wds = [i.strip()
                for i in open(producer_path, encoding="utf-8") if i.strip()]
symptom_wds = [i.strip()
               for i in open(symptom_path, encoding="utf-8") if i.strip()]
region_words = set(disease_wds + department_wds + check_wds +
                   drug_wds + food_wds + producer_wds + symptom_wds)
deny_words = [i.strip()
              for i in open(deny_path, encoding="utf-8") if i.strip()]




# wdtype_dict = dict()
# for word in tqdm(region_words):
#     wdtype_dict[word] = []
#     if word in disease_wds:
#         wdtype_dict[word].append('disease')
#     if word in department_wds:
#         wdtype_dict[word].append('department')
#     if word in check_wds:
#         wdtype_dict[word].append('check')
#     if word in drug_wds:
#         wdtype_dict[word].append('drug')
#     if word in food_wds:
#         wdtype_dict[word].append('food')
#     if word in symptom_wds:
#         wdtype_dict[word].append('symptom')
#     if word in producer_wds:
#         wdtype_dict[word].append('producer')


# # 保存 wdtype_dict 到 Python 文件
# wdtype_dict_file = os.path.join(cur_dir, 'wdtype_dict.py')
# with open(wdtype_dict_file, 'w', encoding='utf-8') as f:
#     f.write('# 医疗词汇类型字典\n')
#     f.write('# 自动生成，请勿手动修改\n\n')
#     f.write('wdtype_dict = {\n')
#     for key, value in wdtype_dict.items():
#         f.write(f'    "{key}": {value},\n')
#     f.write('}\n')

# print(f"wdtype_dict 已保存到: {wdtype_dict_file}")

# 保存 region_words 到 Python 文件
region_words_file = os.path.join(cur_dir, 'region_words.py')
with open(region_words_file, 'w', encoding='utf-8') as f:
    f.write('# 医疗词汇集合\n')
    f.write('# 自动生成，请勿手动修改\n\n')
    f.write('region_words = {\n')
    for word in sorted(region_words):
        f.write(f'    "{word}",\n')
    f.write('}\n')

print(f"region_words 已保存到: {region_words_file}")



