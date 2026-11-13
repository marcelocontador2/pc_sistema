import os

print("🔍 LOCALIZANDO O MAIN.PY PRINCIPAL...\n")
caminho_main_real = None

# Varre as pastas ignorando backups e a venv
for root, dirs, files in os.walk("."):
    if "pc_venv" in root or "_backups" in root or "_arquivo" in root or "__pycache__" in root:
        continue
    if "main.py" in files:
        caminho_main_real = os.path.join(root, "main.py")
        break

if caminho_main_real:
    print(f"✅ Arquivo principal encontrado em: {caminho_main_real}\n")
    print("-" * 60)
    
    with open(caminho_main_real, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        
    inicio_funcao = -1
    for i, linha in enumerate(linhas):
        if 'async def api_integridade_matriz_calcular(' in linha or 'def api_integridade_matriz_calcular(' in linha:
            inicio_funcao = i
            break
            
    if inicio_funcao != -1:
        print(f"➔ FUNÇÃO ENCONTRADA NA LINHA {inicio_funcao + 1}:\n")
        # Imprime a função inteira (120 linhas é o suficiente para ver a lógica toda)
        for j in range(inicio_funcao, min(inicio_funcao + 120, len(linhas))):
            print(f"{j+1}: {linhas[j].rstrip()}")
    else:
        print("❌ Não achei a função 'api_integridade_matriz_calcular' dentro deste arquivo.")

    print("\n" + "-" * 60)
    print("🔍 CONFIGURAÇÃO DE CONEXÃO COM O BANCO:")
    
    # Procura onde o banco é configurado
    for i, linha in enumerate(linhas):
        lower_linha = linha.lower()
        if 'psycopg2.connect' in lower_linha or 'create_engine' in lower_linha or 'def get_db' in lower_linha or 'sqlite3.connect' in lower_linha:
            print(f"Linha {i+1}: {linha.strip()}")
            
else:
    print("❌ Não foi possível encontrar nenhum main.py fora das pastas de backup.")
