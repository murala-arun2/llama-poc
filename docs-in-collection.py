import chromadb
from langchain_ollama import OllamaEmbeddings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_chroma import Chroma

chroma_client = chromadb.HttpClient(host='localhost', port=8000)

ef = OllamaEmbeddingFunction(
    model_name="llama3.2",
    url="http://localhost:11434/api/embeddings",
)


# chroma_client.delete_collection(name="spring-security")

collection = chroma_client.get_collection(name="spring-security-2", embedding_function=ef)

print('docs in collection:', collection.count())

# print('doc :', collection.get(ids=['79e0914b-4b54-4f3b-90e9-6fdf1dc19028']))



# print('docs from query:', collection.query(
#     query_texts=["AuthenicationManager"],
#     # n_results=2,
#     # where={"source": "\\Users\\mural\\Downloads\\spring-security-main\\spring-security-main\\core\\src\\main\\java\\org\\springframework\\security\\access\\AccessDecisionManager.java"}
#     ))

embed = OllamaEmbeddings(
    model="llama3.2"
)
vector_store_from_client = Chroma(
    client=chroma_client,
    collection_name="spring-security-2",
    embedding_function=embed,
    create_collection_if_not_exists=False,
)

print("similarity search:", vector_store_from_client.similarity_search("list down implementations for AuthenticationManager", k=5))