import torch
from transformers import RobertaTokenizer, RobertaModel, pipeline
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
import chromadb
from langchain_chroma import Chroma
from transformers import (RobertaConfig, RobertaModel, RobertaTokenizer)
import torch.nn as nn
from seq2seq_codebert import Seq2Seq
from torch.utils.data import DataLoader, Dataset, SequentialSampler, RandomSampler,TensorDataset

model_name = "microsoft/codebert-base"
args = {
    "max_source_length": 512,
    "max_target_length": 128,
    "num_beams": 4,
    "length_penalty": 2.0,
    "early_stopping": True,
    "no_repeat_ngram_size": 3,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "beam_size": 4
}


config = RobertaConfig.from_pretrained(model_name)
tokenizer = RobertaTokenizer.from_pretrained(model_name)
encoder = RobertaModel.from_pretrained(model_name, config=config)
decoder_layer = nn.TransformerDecoderLayer(d_model=config.hidden_size, nhead=config.num_attention_heads)
decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
model = Seq2Seq(encoder=encoder,decoder=decoder,config=config,
                  beam_size=args["beam_size"],max_length=args["max_target_length"],
                  sos_id=tokenizer.cls_token_id,eos_id=tokenizer.sep_token_id)
model = model.to('cuda')

# pipe = pipeline("feature-extraction", model="microsoft/codebert-base", tokenizer="microsoft/codebert-base", )


# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(host='localhost', port=8000)

# chroma_client.delete_collection(name="spring-security-2")
collection_name = "spring-security-codebert"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Define the path to the Java project source code folder
java_project_path = "E:\\code\\spring-security-main\\spring-security-main\\core\\src\\main\\java"

loader = DirectoryLoader(java_project_path, glob="**/*.java", loader_cls=TextLoader)
docs = loader.load()
print('total java files:', len(docs))
# print('docs[0]:', docs[0])

vector_store_from_client = Chroma(
    client=chroma_client,
    collection_name=collection_name,
    # embedding_function=embed,
    create_collection_if_not_exists=True,
)

# tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
# model = RobertaModel.from_pretrained("microsoft/codebert-base")
# print('model:', model)

# def get_codebert_embedding(code):
#     inputs = tokenizer(code, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
#     with torch.no_grad():
#         outputs = model(**inputs)
#     # return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
#     # decode outputs to get the last hidden states
#     # last_hidden_states = outputs.last_hidden_state
#     # return last_hidden_states
#     # decode last hidden states to get the embeddings
#     # return last_hidden_states.mean(dim=1).squeeze().numpy()
#     # convert embedding to text
#     embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
#     print('code:', code)
#     # print('embeddings:', embeddings)
#     decoded_text = tokenizer.decode(torch.tensor(embeddings).unsqueeze(0))
#     print('decoded text:', decoded_text)
#     # return tokenizer.decode(outputs.last_hidden_states)

# for doc in docs:
#     embedding = get_codebert_embedding(doc.page_content)
#     ids = vector_store_from_client.add_documents(documents=[embedding])
#     print('document id:', ids)



# print(pipe(docs[0].page_content))
# get_codebert_embedding(docs[1].page_content)
# get_codebert_embedding(docs[2].page_content)



source_tokens = tokenizer.tokenize(docs[0].page_content)[:args["max_source_length"]-2]
source_tokens =[tokenizer.cls_token]+source_tokens+[tokenizer.sep_token]
source_ids =  tokenizer.convert_tokens_to_ids(source_tokens) 
source_mask = [1] * (len(source_tokens))
padding_length = args["max_source_length"] - len(source_ids)
source_ids+=[tokenizer.pad_token_id]*padding_length
source_mask+=[0]*padding_length
all_source_ids = torch.tensor([source_ids], dtype=torch.long, device='cuda')
all_source_mask = torch.tensor([source_mask], dtype=torch.long, device='cuda')
# eval_data = TensorDataset(all_source_ids,all_source_mask) 

model.eval() 
      
with torch.no_grad():
    preds = model(source_ids=all_source_ids,source_mask=all_source_mask)  
    for pred in preds:
        t=pred[0].cpu().numpy()
        t=list(t)
        if 0 in t:
            t=t[:t.index(0)]
        text = tokenizer.decode(t,clean_up_tokenization_spaces=False)
        print("")
        print("input :\n", docs[0].page_content)
        print("")
        print('output :\n', text)