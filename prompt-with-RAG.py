from langchain_ollama import OllamaEmbeddings, OllamaLLM
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from graphDB import json_to_graph
from list_of_files_prompt import list_of_files_prompt
import os
import json

llm = OllamaLLM(model="llama3.3")
embeddings = OllamaEmbeddings(model="llama3.3")
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
vector_store = Chroma(embedding_function=embeddings,
                      collection_name="spring-security-10000-llama3.3",
                      client=chroma_client)

prompt_for_class_list =  PromptTemplate(
    template=list_of_files_prompt,
    input_variables=["context", "question"])

promt_with_rag_retrieval = PromptTemplate(
    template=list_of_files_prompt,
    input_variables=["context", "question"])

class State(TypedDict):
    plantuml_class_diagram: str
    ast_json: str
    files_from_llm: List[str]
    files_from_graphdb: List[str]
    files_from_vectordb: List[str]
    question: str
    context: List[Document]
    answer: str

# Define application steps
def load_class_diagram_and_ast_json(state: State):
    print("\nrunning load_class_diagram_and_ast_json ...")
    my_path = os.path.abspath(os.path.dirname(__file__))
    class_diagram_path = os.path.join(my_path, "./plantUML/spring-security-core.puml")
    ast_json_path = os.path.join(my_path, "./plantUML/spring-security-core.json")
    class_diagram = None
    ast_json = None
    with open(class_diagram_path, "r") as file:
        class_diagram = file.read()
    with open(ast_json_path, "r") as file:
        ast_json = file.read()
    print("class diagram size: ", len(class_diagram))
    print("ast json size :", len(ast_json))
    return { 
        "plantuml_class_diagram": class_diagram,
        "ast_json": ast_json
    }

def get_call_chain_from_llm(state: State):
    print("\nrunning get_call_chain_from_llm ...")
    messages = prompt_for_class_list.invoke({"question": state["question"], "context": state["plantuml_class_diagram"]})
    response = llm.invoke(messages)
    print("files considerations response :\n", response)
    files_list = [line.strip().replace("- ", "") for line in response.split('\n') if line.startswith('- ')]
    print('files_list from llm :', files_list)
    return {"files_from_llm": files_list}

def get_call_chain_from_graphdb(state: State):
    print("\nrunning get_call_chain_from_graphdb ...")
    g = json_to_graph.construct_graph(json.loads(state["ast_json"]))
    call_chain = json_to_graph.find_call_chain(g, "SecurityConfig::getAttribute") # TODO get from user question
    print('call_chain :', call_chain)
    files_list = [obj.get("id").split("::")[0] for obj in call_chain.get("result")]
    print('files_list from graphdb :', files_list)
    return { "files_from_graphdb" : files_list }

def retrieve_from_vectordb(state: State):
    print("\nrunning retrieve_from_vectordb ...")
    retrieved_docs = vector_store.similarity_search(state["question"])
    print("retrieved_docs :\n", retrieved_docs)
    return {}


# def generate_response(state: State):
#     docs_content = "\n\n".join(doc.page_content for doc in state["context"])
#     messages = prompt.invoke({"question": state["question"], "context": docs_content})
#     print("messages :\n", messages)
#     response = llm.invoke(messages)
#     print("response :\n", response)
#     return {"answer": response}

# state = State({
#     "question": "explain code flow to AuthorityAuthorizationManager.check() method"
# })
# state = attach_ast_and_get_recommendation(state)

# state = State({
#     "question": "explain code flow to AuthorityAuthorizationManager.check() method based the class diagram"
# })
# state = attach_ast_and_get_recommendation(state)

# def main():
# Compile application and test
graph_builder = StateGraph(State).add_sequence([
    load_class_diagram_and_ast_json, 
    get_call_chain_from_llm,
    get_call_chain_from_graphdb,
    retrieve_from_vectordb,
    ])
graph_builder.add_edge(START, "load_class_diagram_and_ast_json")
graph = graph_builder.compile()
response = graph.invoke({"question": """list of classes that are involved in data flow to below method
    ```plantuml
    SecurityConfig::getAttribute```
    """})
# print(response["answer"])

# if __name__ == '__main__':
#     main()