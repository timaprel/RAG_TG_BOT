from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "IlyaGusev/saiga_llama3_8b"

print("Downloading tokenizer...")
AutoTokenizer.from_pretrained(model_name)

print("Downloading model...")
AutoModelForCausalLM.from_pretrained(model_name)

print("Done!")