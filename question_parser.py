import ahocorasick
from dict.wdtype_dict import wdtype_dict
from dict.region_words import region_words


question = "肺气肿和百日咳要做血常规吗?"

'''构造AC自动机，加速过滤'''
def build_actree(wordlist):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(wordlist):
        actree.add_word(word, (index, word))
    actree.make_automaton()
    return actree


# 构造AC自动机
region_tree = build_actree(list(region_words))


question_entity = []
for each in region_tree.iter(question):
    print(each)
    entity = each[1][1]
    question_entity.append(entity)
print(question_entity)

question_entity_dict = {each:wdtype_dict[each] for each in question_entity}

