import chromadb
import os
from dotenv import load_dotenv
from utils.embedding_model import EmbeddingModel

load_dotenv()

class ChromaEmbeddingFunction:
    """
    将本地 EmbeddingModel 适配为 Chroma 的 embedding_function 接口：
    可调用对象，输入 List[str] 或 str，返回 List[List[float]]。
    """

    def __init__(self):
        self._model = EmbeddingModel()

    def __call__(self, input):
        if isinstance(input, str):
            return [self._model.create_embeddings(input)]
        return self._model.create_embeddings(input)
    
    def embed_query(self, input):
        """ChromaDB 查询时使用的嵌入方法"""
        if isinstance(input, str):
            return self._model.create_embeddings(input)
        elif isinstance(input, list):
            return self._model.create_embeddings(input)
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")
    
    def embed_documents(self, input):
        """ChromaDB 文档嵌入时使用的方法"""
        if isinstance(input, str):
            return [self._model.create_embeddings(input)]
        elif isinstance(input, list):
            return self._model.create_embeddings(input)
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")
    
    def name(self):
        """ChromaDB 要求的 name 方法"""
        return "custom_embedding_function"


emb_fn = ChromaEmbeddingFunction()

# 持久化客户端
data_path = os.path.join(os.getcwd(), os.getenv("CHROME_LOCAL_PATH"))
client = chromadb.PersistentClient(path=data_path)

collection = client.get_or_create_collection(
    name="example",
    embedding_function=emb_fn
)

# 添加中文文档
collection.add(
    documents=[
        "深度学习是人工智能的一个重要分支。",
        "Python 是一种广泛使用的高级编程语言。",
        "杭州是中国的电子商务中心，阿里巴巴总部所在地。"
    ],
    metadatas=[
        {"topic": "AI"},
        {"topic": "Programming"},
        {"topic": "City"}
    ],
    ids=["1", "2", "3"]
)

# 查询
results = collection.query(query_texts=["阿里巴巴在哪个城市？"], n_results=1)
print("最相关文档:", results['documents'][0])