from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

'''
Module for loading and querying the LLM. Feel free to gut it and turn it into a wrapper for your own LLM pipeline. The only thing the other modules
expect to be present is the 'generate' function, with the option to set a maximum token length for the models responses.

It is worth noting that this implementation does not support token streaming. Adding it would require substantial changes here, as well as in the HTTP server and client.
As such, request and responses must be sent and recieved atomically.

I intend on creating a version that supports token streaming later on. But since it's not needed in every use case, I feel that supporting it would add unnecessary complexity here.
'''

# MODEL DEPENDENT PARAMETERS
MODEL_ID = "google/gemma-2-9b-it"
START_OF_TURN_MARKER = "<start_of_turn>model"
END_OF_TURN_MARKER = "<end_of_turn>"
MAXIMUM_CONTEXT_LENGTH = 8192

# Optional: 4 bit integer quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    quantization_config=bnb_config,
    low_cpu_mem_usage=True
)

# Note that errors should not be caught within this function because resource_profile will need to detect them.
# If an error occurs during regular usage, it should be caught in server.py and the client should be informed that
# an internal server error occured.
def generate(chat, max_new):
    prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
    outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=max_new)
    text = tokenizer.decode(outputs[0])

    response = text.split(START_OF_TURN_MARKER)[-1].split(END_OF_TURN_MARKER)[0].strip()
    
    print("RESPONSE:",response)
    return response
