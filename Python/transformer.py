from transformers import pipeline, AutoTokenizer, AutoModel

checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)

raw_inputs = [
    "I've been waiting for a HuggingFace course my whole life.",
    "I hate this so much!",
]

inputs = tokenizer(raw_inputs, padding=True, truncation=True, return_tensors="pt")
print(inputs)

model = AutoModel.from_pretrained(checkpoint)

outputs = model(**inputs)

print(outputs.last_hidden_state.shape)
