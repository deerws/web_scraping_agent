import subprocess


try:
    print("Executando o script 1: Coletar dados...")
    subprocess.run(["python", "inserir_dados_mysql.py"], check=True)


    print("Executando o script 2: Eliminar duplicatas...")
    subprocess.run(["python", "eliminar_duplicatas.py"], check=True)


    print("Executando o script 3: Enviar para MySQL...")
    subprocess.run(["python", "inserir_dados_mysql.py"], check=True)


    print("Todos os scripts executados com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar o script: {e}")