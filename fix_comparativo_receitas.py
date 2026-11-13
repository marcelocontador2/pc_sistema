import os
import re

# Caminho provável do backend
backend_path = "pc_backend/main.py"

if not os.path.exists(backend_path):
    print("ERRO: Arquivo main.py não encontrado na pasta pc_backend.")
    exit()

with open(backend_path, "r", encoding="utf-8") as f:
    content = f.read()

# Faz um backup do main.py antes de alterar
with open(backend_path + ".bak_rotas", "w", encoding="utf-8") as f:
    f.write(content)

alterado = False

# 1. Procura a função da rota de comparativo de receitas
# Geralmente o nome da função contém 'comparativo_receitas'
padrao_rota = r'(@app\.route\([\'"]/analise_comparativo_receitas[\'"]\).*?def\s+(\w+)\()'
match = re.search(padrao_rota, content, re.DOTALL | re.IGNORECASE)

if match:
    nome_funcao = match.group(2)
    print(f"✅ Rota encontrada na função: {nome_funcao}")
    
    # 2. Vamos procurar por comandos SQLite comuns dentro dessa função e substituir por PostgreSQL
    # Pega o bloco da função (até a próxima rota ou fim do arquivo)
    inicio_funcao = match.start()
    proxima_rota = content.find("@app.route", match.end())
    
    if proxima_rota == -1:
        bloco_funcao = content[inicio_funcao:]
    else:
        bloco_funcao = content[inicio_funcao:proxima_rota]

    bloco_original = bloco_funcao

    # Substituições comuns de SQLite para PostgreSQL:
    # - Trocar '?' por '%s' nos parâmetros de query
    bloco_funcao = bloco_funcao.replace("?", "%s")
    
    # - Trocar funções de data do SQLite (strftime) por PostgreSQL (TO_CHAR ou EXTRACT), se houver
    bloco_funcao = re.sub(r"strftime\('%Y',\s*([^)]+)\)", r"EXTRACT(YEAR FROM \1)", bloco_funcao)
    bloco_funcao = re.sub(r"strftime\('%m',\s*([^)]+)\)", r"EXTRACT(MONTH FROM \1)", bloco_funcao)
    
    # - Se houver conexão com sqlite3, avisar (mas não alterar automaticamente para não quebrar)
    if "sqlite3.connect" in bloco_funcao:
        print("⚠️ ATENÇÃO: A função ainda usa 'sqlite3.connect'. Isso precisa ser mudado para o psycopg2/PostgreSQL.")
        # Exemplo de substituição (pode precisar de ajuste fino dependendo do seu código)
        bloco_funcao = bloco_funcao.replace("sqlite3.connect", "# sqlite3.connect removido - usar db_postgres")

    if bloco_funcao != bloco_original:
        content = content.replace(bloco_original, bloco_funcao)
        alterado = True
        print("✅ Query da rota atualizada para o padrão PostgreSQL (substituição de '?' por '%s').")
    else:
        print("ℹ️ Nenhuma alteração de sintaxe SQLite foi necessária na query (pode já estar em PostgreSQL ou usar ORM).")

else:
    print("❌ Rota '/analise_comparativo_receitas' não encontrada no main.py. Pode estar em outro arquivo (ex: routes.py).")

if alterado:
    with open(backend_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Arquivo main.py salvo com sucesso! Reinicie o servidor backend para testar.")
else:
    print("Nenhuma alteração foi salva no arquivo.")

