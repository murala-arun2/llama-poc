from transformers import RobertaForMaskedLM, RobertaTokenizer
import torch

model = RobertaForMaskedLM.from_pretrained('microsoft/codebert-base-mlm')
tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base-mlm')

# Tokenize input code and natural language
nl_tokens = tokenizer.tokenize("<mask>")
code_tokens = tokenizer.tokenize("def max(a,b): if a>b: return a else return b")

# Prepare token list
tokens = [tokenizer.cls_token] + nl_tokens + [tokenizer.sep_token] + code_tokens + [tokenizer.eos_token]
token_ids = tokenizer.convert_tokens_to_ids(tokens)

# Run inference
with torch.no_grad():
    # Convert token IDs to tensor and add batch dimension
    input_tensor = torch.tensor(token_ids)[None, :]
    
    # Get model output (logits)
    outputs = model(input_tensor)
    logits = outputs.logits  # Get logits (raw predictions)

    # Get the most probable token IDs for each position (argmax over vocab dimension)
    predicted_ids = torch.argmax(logits, dim=-1)

    # Remove the batch dimension and get token IDs for the sequence
    predicted_token_ids = predicted_ids[0].cpu().numpy()

    # Decode the predicted token IDs into text
    decoded_text = tokenizer.decode(predicted_token_ids, skip_special_tokens=True)

    print("\nGenerated Documentation Comment:\n", decoded_text)
