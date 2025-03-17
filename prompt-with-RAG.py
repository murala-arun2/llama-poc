from langchain_ollama import OllamaEmbeddings, OllamaLLM
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate


llm = OllamaLLM(model="llama3.2")
embeddings = OllamaEmbeddings(model="llama3.2")
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
vector_store = Chroma(embedding_function=embeddings,
                      collection_name="spring-security-2",
                      client=chroma_client)
prompt = PromptTemplate(
    template="""You are a java expert.
Assume you dont have any knowledge of spring security framework.
Asnwer the user question based on the Context provided only.
Question: {question}
Context: {context}""",
input_variables=["question", "context"],)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    print("state['question'] :\n", state["question"])
    retrieved_docs = vector_store.similarity_search(state["question"])
    print("retrieved_docs :\n", retrieved_docs)
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    print("messages :\n", messages)
    response = llm.invoke(messages)
    print("response :\n", response)
    return {"answer": response}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
response = graph.invoke({"question": "list down implementations for AuthenticationManager"})
# print(response["answer"])