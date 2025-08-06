import json

def montar_prompt(exemplos, objetivo, url, info_api=None):
    prompt = "Você é um gerador de código Python para scraping com Playwright ou requests.\n\n"
    for ex in exemplos:
        prompt += f"Objetivo: {ex['objetivo']}\n"
        prompt += f"URL: {ex['url']}\n"
        prompt += f"Tecnologia: {ex['tecnologia_usada']}\n"
        prompt += f"Código:\n{ex['codigo']}\n---\n"
    prompt += f"\nNovo objetivo: {objetivo}\nURL alvo: {url}\n"
    if info_api:
        prompt += f"\nEndpoint detectado: {info_api['url']}\n"
        prompt += f"Exemplo de resposta:\n{json.dumps(info_api['json'], indent=2)}\n"
    prompt += "\nGere o código Python correspondente para realizar o scraping."
    return prompt
