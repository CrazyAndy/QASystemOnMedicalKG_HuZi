import os
from tqdm import tqdm
import json

from utils.chroma_utils import ChromeUtils
from utils.logger_utils import info
from utils.neo4j_utils import Neo4jUtils, Node, Relationship

data_path = os.getcwd() + '/data/medical.json'
graph_db_utils = Neo4jUtils()
chroma_utils = ChromeUtils()

def read_nodes(data_path):
    # 共７类节点
    drugs = []  # 药品
    foods = []  # 　食物
    checks = []  # 检查
    departments = []  # 科室
    producers = []  # 药品大类
    diseases = []  # 疾病
    symptoms = []  # 症状

    disease_infos = []  # 疾病信息

    # 构建节点实体关系
    rels_department = []  # 　科室－科室关系
    rels_noteat = []  # 疾病－忌吃食物关系
    rels_doeat = []  # 疾病－宜吃食物关系
    rels_recommandeat = []  # 疾病－推荐吃食物关系
    rels_commonddrug = []  # 疾病－通用药品关系
    rels_recommanddrug = []  # 疾病－热门药品关系
    rels_check = []  # 疾病－检查关系
    rels_drug_producer = []  # 厂商－药物关系

    rels_symptom = []  # 疾病症状关系
    rels_acompany = []  # 疾病并发关系
    rels_category = []  # 　疾病与科室之间的关系

    count = 0
    for data in open(data_path):
        disease_dict = {}
        count += 1
        print(count)
        data_json = json.loads(data)
        disease = data_json['name']
        disease_dict['name'] = disease
        diseases.append(disease)
        disease_dict['desc'] = ''
        disease_dict['prevent'] = ''
        disease_dict['cause'] = ''
        disease_dict['easy_get'] = ''
        disease_dict['cure_department'] = ''
        disease_dict['cure_way'] = ''
        disease_dict['cure_lasttime'] = ''
        disease_dict['symptom'] = ''
        disease_dict['cured_prob'] = ''

        if 'symptom' in data_json:
            symptoms += data_json['symptom']
            for symptom in data_json['symptom']:
                rels_symptom.append([disease, symptom])

        if 'acompany' in data_json:
            for acompany in data_json['acompany']:
                rels_acompany.append([disease, acompany])

        if 'desc' in data_json:
            disease_dict['desc'] = data_json['desc']

        if 'prevent' in data_json:
            disease_dict['prevent'] = data_json['prevent']

        if 'cause' in data_json:
            disease_dict['cause'] = data_json['cause']

        if 'get_prob' in data_json:
            disease_dict['get_prob'] = data_json['get_prob']

        if 'easy_get' in data_json:
            disease_dict['easy_get'] = data_json['easy_get']

        if 'cure_department' in data_json:
            cure_department = data_json['cure_department']
            if len(cure_department) == 1:
                rels_category.append([disease, cure_department[0]])
            if len(cure_department) == 2:
                big = cure_department[0]
                small = cure_department[1]
                rels_department.append([small, big])
                rels_category.append([disease, small])

            disease_dict['cure_department'] = cure_department
            departments += cure_department

        if 'cure_way' in data_json:
            disease_dict['cure_way'] = data_json['cure_way']

        if 'cure_lasttime' in data_json:
            disease_dict['cure_lasttime'] = data_json['cure_lasttime']

        if 'cured_prob' in data_json:
            disease_dict['cured_prob'] = data_json['cured_prob']

        if 'common_drug' in data_json:
            common_drug = data_json['common_drug']
            for drug in common_drug:
                rels_commonddrug.append([disease, drug])
            drugs += common_drug

        if 'recommand_drug' in data_json:
            recommand_drug = data_json['recommand_drug']
            drugs += recommand_drug
            for drug in recommand_drug:
                rels_recommanddrug.append([disease, drug])

        if 'not_eat' in data_json:
            not_eat = data_json['not_eat']
            for _not in not_eat:
                rels_noteat.append([disease, _not])

            foods += not_eat
            do_eat = data_json['do_eat']
            for _do in do_eat:
                rels_doeat.append([disease, _do])

            foods += do_eat
            recommand_eat = data_json['recommand_eat']

            for _recommand in recommand_eat:
                rels_recommandeat.append([disease, _recommand])
            foods += recommand_eat

        if 'check' in data_json:
            check = data_json['check']
            for _check in check:
                rels_check.append([disease, _check])
            checks += check
        if 'drug_detail' in data_json:
            drug_detail = data_json['drug_detail']
            producer = [i.split('(')[0] for i in drug_detail]
            rels_drug_producer += [[i.split('(')[0], i.split(
                '(')[-1].replace(')', '')] for i in drug_detail]
            producers += producer
        disease_infos.append(disease_dict)
    return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos, \
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, \
        rels_symptom, rels_acompany, rels_category


'''建立节点'''


def create_node_by_label_and_nodes(label, node_names):
    nodes = []
    for node_name in node_names:
        properties = {'name': node_name}
        result = graph_db_utils.create_node(label, properties)
        if result['success']:
            nodes.append(result['node'])
    return nodes


'''创建知识图谱中心疾病的节点'''


def create_diseases_nodes(disease_infos):
    nodes = []
    for disease_dict in disease_infos:
        properties = {
            'name': disease_dict['name'],
            'desc': disease_dict['desc'],
            'prevent': disease_dict['prevent'],
            'cause': disease_dict['cause'],
            'easy_get': disease_dict['easy_get'],
            'cure_lasttime': disease_dict['cure_lasttime'],
            'cure_department': disease_dict['cure_department'],
            'cure_way': disease_dict['cure_way'],
            'cured_prob': disease_dict['cured_prob']
        }
        result = graph_db_utils.create_node("Disease", properties)
        if result['success']:
            nodes.append(result['node'])
    return nodes


'''创建实体关联边'''


def create_relationship(start_node, end_node, edges, rel_type, rel_name):
    relationships = []
    count = 0
    # 去重处理
    set_edges = []
    for edge in edges:
        set_edges.append('###'.join(edge))
    all = len(set(set_edges))
    for edge in set(set_edges):
        edge = edge.split('###')
        p = edge[0]
        q = edge[1]
        from_node = {'label': start_node, 'properties': {'name': p}}
        to_node = {'label': end_node, 'properties': {'name': q}}
        try:
            result = graph_db_utils.create_relationship(
                from_node, rel_type, to_node, properties={'name': rel_name})
            if result['success']:
                relationships.append(result['relationship'])
            count += 1
            print(rel_type, count, all)
        except Exception as e:
            print(e)

    return relationships


def insert_nodes_2_chroma(nodes):
    for node in nodes:
        if isinstance(node, Node):
            print(f"插入节点: {node.labels} {node.id}")
            chroma_utils.add_document(
                node.labels,
                {"type":"entity","topic": node.labels[0]},
                [str(node.id)])


def insert_relationships_2_chroma(relationships):
    for relationship in relationships:
        if isinstance(relationship, Relationship):
            chroma_utils.add_document(
                relationship.type,
                {"type":"relationship","topic": relationship.type[0]},
                [str(relationship.id)])


if __name__ == "__main__":
    # 0，清空数据库
    graph_db_utils.delete_all_nodes_and_relationships()

    # 1，解析文档 获取节点 和 关系
    drugs, foods, checks, departments, producers, symptoms, diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = read_nodes(
        data_path)

    info(f"1、解析文档 获取节点 和 关系 完成")

    # 2，创建疾病节点
    diseases_nodes = create_diseases_nodes(disease_infos)
    info(f"2、创建疾病节点 完成")

    # 3，创建药品、食物、检查、科室、生产商、症状节点
    drugs_nodes = create_node_by_label_and_nodes("Drug", drugs)
    # foods_nodes = create_node_by_label_and_nodes("Food", foods)
    # checks_nodes = create_node_by_label_and_nodes("Check", checks)
    # departments_nodes = create_node_by_label_and_nodes(
    #     "Department", departments)
    # producers_nodes = create_node_by_label_and_nodes("Producer", producers)
    symptoms_nodes = create_node_by_label_and_nodes("Symptom", symptoms)
    info(f"3、创建药品、食物、检查、科室、生产商、症状节点 完成")

    # 4、创建实体关系
    # rels_recommandeat_nodes = create_relationship('Disease', 'Food', rels_recommandeat,
    #                                               'recommand_eat', '推荐食谱')
    # rels_noteat_nodes = create_relationship(
    #     'Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
    # rels_doeat_nodes = create_relationship(
    #     'Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
    # rels_department_nodes = create_relationship('Department', 'Department',
    #                                             rels_department, 'belongs_to', '属于')
    # rels_commonddrug_nodes = create_relationship('Disease', 'Drug', rels_commonddrug,
    #                                              'common_drug', '常用药品')
    # rels_drug_producer_nodes = create_relationship('Producer', 'Drug',
    #                                                rels_drug_producer, 'drugs_of', '生产药品')
    rels_recommanddrug_nodes = create_relationship('Disease', 'Drug', rels_recommanddrug,
                                                   'recommand_drug', '好评药品')
    # rels_check_nodes = create_relationship(
    #     'Disease', 'Check', rels_check, 'need_check', '诊断检查')
    rels_symptom_nodes = create_relationship('Disease', 'Symptom',
                                             rels_symptom, 'has_symptom', '症状')
    # rels_acompany_nodes = create_relationship('Disease', 'Disease',
    #                                           rels_acompany, 'acompany_with', '并发症')
    # rels_category_nodes = create_relationship('Disease', 'Department',
    #                                           rels_category, 'belongs_to', '所属科室')
    info(f"4、创建实体关系 完成")

    insert_nodes_2_chroma(diseases_nodes)
    insert_nodes_2_chroma(drugs_nodes)
    # insert_nodes_2_chroma(foods_nodes)
    # insert_nodes_2_chroma(checks_nodes)
    # insert_nodes_2_chroma(departments_nodes)
    # insert_nodes_2_chroma(producers_nodes)
    insert_nodes_2_chroma(symptoms_nodes)
    
    info(f"5、插入节点到chroma 完成")
    
    # insert_relationships_2_chroma(rels_recommandeat_nodes)
    # insert_relationships_2_chroma(rels_noteat_nodes)
    # insert_relationships_2_chroma(rels_doeat_nodes)
    # insert_relationships_2_chroma(rels_department_nodes)
    # insert_relationships_2_chroma(rels_commonddrug_nodes)
    # insert_relationships_2_chroma(rels_drug_producer_nodes)
    insert_relationships_2_chroma(rels_recommanddrug_nodes)
    # insert_relationships_2_chroma(rels_check_nodes)
    insert_relationships_2_chroma(rels_symptom_nodes)
    # insert_relationships_2_chroma(rels_acompany_nodes)
    # insert_relationships_2_chroma(rels_category_nodes)
    info(f"6、插入关系到chroma 完成")
    
    
    
    
