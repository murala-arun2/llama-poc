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
    # model="llama3.2"
    model="starcoder2"
)

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# chroma_client.delete_collection(name="spring-security-2")
# collection_name = "spring-security-4"
collection_name = "spring-security-10000-starcoder2"
# collection_name = "hertzbeat-manager-10000"
# collection_name = "hertzbeat-manager-startcoder2-10000"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Define the path to the Java project source code folder
java_project_path = "E:\\code\\spring-security-main\\spring-security-main\\core\\src\\main\\java"
# java_project_path = "C:\\Users\\pc\\Downloads\\hertzbeat-master\\hertzbeat-master\\hertzbeat-manager\\src\\main\\java"

loader = DirectoryLoader(java_project_path, glob="**/*.java", loader_cls=TextLoader)
docs = loader.load()
print('total java files:', len(docs))
# print('docs[0]:', docs[0])

# splitter = RecursiveCharacterTextSplitter.from_language(
#     language=Language.JAVA, chunk_size=500, chunk_overlap=0
# )

splitter = RecursiveCharacterTextSplitter(separators=[
                # Split along class definitions
                "\\s*class ",
                # Split along method definitions
                "\\s*public ",
                "\\s*protected ",
                "\\s*private ",
                "\\s*static "], keep_separator=True, is_separator_regex=True, chunk_size=10000, chunk_overlap=0)

all_splits = splitter.split_documents(docs)
print('files after split:', len(all_splits))


vector_store_from_client = Chroma(
    client=chroma_client,
    collection_name=collection_name,
    embedding_function=embed,
    create_collection_if_not_exists=True,
)

for doc in all_splits:
    ids = vector_store_from_client.add_documents(documents=[doc])
    print('document id:', ids)
# ids = vector_store_from_client.add_documents(documents=all_splits)

