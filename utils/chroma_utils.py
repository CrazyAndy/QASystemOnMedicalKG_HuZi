from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb
import os
from dotenv import load_dotenv
load_dotenv()


class ChromeUtils:
    def __init__(self):
        model_path = os.getenv("LOCAL_MODEL_PATH", None)
        chroma_path = os.getcwd() + f'/.{os.getenv("CHROME_LOCAL_PATH")}'
        # 使用中文 embedding 模型
        self.emb_fn = SentenceTransformerEmbeddingFunction(model_path)
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="example",
            embedding_function=self.emb_fn
        )

    def add_document(self, document, metadata,ids):
        self.collection.add(
            documents=document,
            metadatas=metadata,
            ids=ids
        )

    def query_document(self, query,type, n_results=1):
        return self.collection.query(query_texts=[query], n_results=n_results,where={"type": type})


# # 添加中文文档
# collection.add(
#     documents=[
#         "深度学习是人工智能的一个重要分支。",
#         "Python 是一种广泛使用的高级编程语言。",
#         "杭州是中国的电子商务中心，阿里巴巴总部所在地。"
#     ],
#     metadatas=[
#         {"topic": "AI"},
#         {"topic": "Programming"},
#         {"topic": "City"}
#     ],
#     ids=["1", "2", "3"]
# )

# # 查询
# results = collection.query(query_texts=["阿里巴巴在哪个城市？"], n_results=1)
# print("最相关文档:", results['documents'][0])
