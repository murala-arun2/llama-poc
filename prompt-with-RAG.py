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
                      collection_name="spring-security-4",
                      client=chroma_client)

prompt_for_ast_test =  PromptTemplate(
    template="""Human: you are a java programmer without any knowledge of spring security framework. below is class diagram of a java project in plantuml format. \n
{context} \n\n
Question: {question} """,
input_variables=["context", "question"],)

prompt_for_ast_to_files_needed =  PromptTemplate(
    template="""Context: you are a java programmer without any knowledge of spring security framework. below is class diagram of a java project in plantuml format. \n
{context} \n\n
Question: You need to analyze the class diagram and identify the classes that are needed to answer the question. you are a java developer. you are asked to list down the classes that you need need to inspect full source code of java classes to answer below question. Generate a response as list class names only and dont output any description about the project \n
{question} \n\n
Output format: <package>.<class_name>, <package>.<class_name>, <package>.<class_name> \n
Sample output: org.springframework.security.access.intercept.AbstractSecurityInterceptor, org.springframework.security.access.intercept.RunAsManagerImpl, org.springframework.security.access.intercept.aopalliance.MethodSecurityInterceptor""",
input_variables=["context", "question"],)

prompt = PromptTemplate(
    template="""You are a java developer.
You dont have any knowledge of spring security framework.
Asnwer the user question based on the Context provided only.
Question: {question}
Context: {context}""",
input_variables=["question", "context"],)

class State(TypedDict):
    ast: str
    question: str
    files_to_consider: List[str]
    context: List[Document]
    answer: str


# Define application steps
def attach_ast_and_get_recommendation(state: State):
    with open("output.puml", "r") as file:
        content = file.read()
        print("class diagram read from file")
        # messages = prompt_for_ast_to_files_needed.invoke({"question": state["question"], "context": content})
        messages = prompt_for_ast_test.invoke({"question": state["question"], "context": content})
        print("messages :\n", messages)
        response = llm.invoke(messages)
        print("files considerations response :\n", response)

        return {"files_to_consider": response}

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
# graph_builder = StateGraph(State).add_sequence([retrieve, generate])
# graph_builder.add_edge(START, "retrieve")
# graph = graph_builder.compile()
# response = graph.invoke({"question": "explain code flow to AuthorityAuthorizationManager.check() method"})
# print(response["answer"])

# state = State({
#     "question": "explain code flow to AuthorityAuthorizationManager.check() method"
# })
# state = attach_ast_and_get_recommendation(state)

state = State({
    "question": "explain code flow to AuthorityAuthorizationManager.check() method based the class diagram"
})
state = attach_ast_and_get_recommendation(state)