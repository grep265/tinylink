from llama_cpp import Llama

MODEL_PATH = "./models/TinyLink.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_threads=8,
    n_ctx=2048,
    n_batch=64,
    verbose=False
)

def generate_response(prompt: str) -> str:
    """
    Generate LLM response
    """
    prompt_text = f"Human: {prompt}\nAssistant:"
    output = llm(
        prompt_text,
        max_tokens=25,
        temperature=0.1,
        stop=["}"]
    )
    
    model_output = output["choices"][0]["text"].strip()
    
    response_start = model_output.find("{")
    response_end = model_output.find("}")
    
    if response_start != -1:
        if response_end == -1 or not model_output.endswith("}"):
            model_output = model_output[response_start:] + "}"
        else:
            model_output = model_output[response_start:response_end + 1]
            
    return model_output