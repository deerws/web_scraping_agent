import subprocess

def executar_codigo(codigo_str, nome_arquivo="scraper_temp.py"):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(codigo_str)
    print(f"🚀 Executando {nome_arquivo}...")
    subprocess.run(["python", nome_arquivo])
