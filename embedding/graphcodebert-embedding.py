from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
import torch
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = RobertaTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = RobertaModel.from_pretrained("microsoft/graphcodebert-base")
model.to(device)

# Initialize the document loader to read Java files
# Define the path to the Java project source code folder
java_project_path = "E:\\code\\spring-security-main\\spring-security-main\\core\\src\\main\\java"

loader = DirectoryLoader(java_project_path, glob="**/*.java", loader_cls=TextLoader)
docs = loader.load()
print('total java files:', len(docs))
print('docs[0]:', docs[0])

# # Initialize the GraphCodeBERT embedder
for doc in docs[:1]:
    tokens = tokenizer.tokenize(doc.page_content)
    print('tokens:\n', tokens)
    tokens_ids=tokenizer.convert_tokens_to_ids(tokens)
    print('tokens_ids:\n', tokens_ids)
    context_embeddings=model(torch.tensor(tokens_ids)[None,:])[0]
    print('context_embeddings:\n', context_embeddings)
    # inputs.to(device)
    # outputs = model(**inputs)
    # embeddings = outputs.last_hidden_state.mean(dim=1)
    # print('embeddings:', embeddings)

# # Convert documents to embeddings
# embeddings = [embedder.embed(document) for document in docs[:5]]
# print('embeddings:', embeddings)

# # convert embedding back readable text  (optional)
# decoded = [embedder.decode(embedding) for embedding in embeddings] 
# print('decoded:', decoded)


