from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

embed = OllamaEmbeddings(
    model="llama3.2"
)

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# chroma_client.delete_collection(name="spring-security-2")

collection = chroma_client.get_or_create_collection(name="spring-security-2")

# Define the path to the Java project source code folder
java_project_path = "E:\\code\\spring-security-main\\spring-security-main\\core\\src\\main\\java"

loader = DirectoryLoader(java_project_path, glob="**/*.java", loader_cls=TextLoader)
docs = loader.load()
print('total java files:', len(docs))
print('docs[0]:', docs[0])

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JAVA, chunk_size=500, chunk_overlap=0
)
all_splits = splitter.split_documents(docs)
print('files after split:', len(all_splits))


vector_store_from_client = Chroma(
    client=chroma_client,
    collection_name="spring-security-2",
    embedding_function=embed,
    create_collection_if_not_exists=True,
)

for doc in all_splits:
    ids = vector_store_from_client.add_documents(documents=[doc])
    print('document id:', ids)
# ids = vector_store_from_client.add_documents(documents=all_splits)

