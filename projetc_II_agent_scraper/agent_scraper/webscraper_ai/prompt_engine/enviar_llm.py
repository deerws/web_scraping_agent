import requests

def enviar_para_llama(prompt):
    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "codellama:7b", "prompt": prompt, "stream": False}
    )
    return resposta.json()["response"]
