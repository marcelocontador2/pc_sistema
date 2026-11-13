import re

caminho_main = "main.py"

try:
    with open(caminho_main, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    print("🔍 EXTRAINDO O CÓDIGO DA ROTA DE INTEGRIDADE DO ARQUIVO MAIN.PY:\n")
    
    # Procura a definição da rota
    inicio_funcao = -1
    for i, linha in enumerate(linhas):
        if 'async def api_integridade_matriz_calcular(' in linha or 'def api_integridade_matriz_calcular(' in linha:
            inicio_funcao = i
            break
            
    if inicio_funcao != -1:
        print(f"Encontrado na linha {inicio_funcao + 1} do main.py.")
        print("-" * 60)
        # Imprime as próximas 120 linhas para pegar toda a função (queries, conexão, etc)
        for j in range(inicio_funcao, min(inicio_funcao + 120, len(linhas))):
            print(f"{j+1}: {linhas[j].rstrip()}")
        print("-" * 60)
    else:
        print("❌ Função 'api_integridade_matriz_calcular' não encontrada no main.py raiz.")

    print("\n🔍 BUSCANDO A CONFIGURAÇÃO DO POSTGRESQL:\n")
    # Procura como o banco é conectado
    for i, linha in enumerate(linhas):
        if 'postgres' in linha.lower() or 'psycopg2' in linha.lower() or 'sqlalchemy' in linha.lower() or 'DATABASE_URL' in linha:
            print(f"Linha {i+1}: {linha.strip()}")

except FileNotFoundError:
    print("❌ Arquivo main.py não encontrado no diretório atual. Verifique o caminho.")
