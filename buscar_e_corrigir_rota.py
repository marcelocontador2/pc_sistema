import os
import re

backend_dir = "pc_backend"
rota_alvo = "/analise_comparativo_receitas"

# Procura em todos os arquivos .py da pasta pc_backend (e subpastas)
arquivos_encontrados = []
for root, dirs, files in os.walk(backend_dir):
    # Ignora pastas de backup/venv
    dirs[:] = [d for d in dirs if not d.startswith("__") and "venv" not in d and "backup" not in d]
    for file in files:
        if file.endswith(".py"):
            caminho = os.path.join(root, file)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                if rota_alvo in conteudo:
                    arquivos_encontrados.append(caminho)
            except Exception as e:
                pass

if not arquivos_encontrados:
    print(f"❌ Rota '{rota_alvo}' não encontrada em nenhum arquivo .py da pasta {backend_dir}.")
    print("Verifique manualmente qual arquivo contém essa rota.")
    exit()

print(f"✅ Rota encontrada nos seguintes arquivos:")
for arq in arquivos_encontrados:
    print(f"   - {arq}")

# Agora vamos corrigir todos os arquivos encontrados
for caminho_arquivo in arquivos_encontrados:
    print(f"\n🔧 Corrigindo: {caminho_arquivo}")
    
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Backup
    with open(caminho_arquivo + ".bak_rotas", "w", encoding="utf-8") as f:
        f.write(content)
    
    alterado = False
    
    # Procura a função que responde à rota
    padrao_rota = r'(@(?:app|bp|blueprint|route)\.route\(\s*[\'"]' + re.escape(rota_alvo) + r'[\'"].*?def\s+(\w+)\()'
    match = re.search(padrao_rota, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        nome_funcao = match.group(1)
        print(f"   Função encontrada: {nome_funcao}")
        
        inicio_funcao = match.start()
        # Procura próxima rota ou decorator após o início da função
        proxima_rota = content.find("@app.route", match.end())
        proxima_bp = content.find("@bp.route", match.end())
        proxima_decorator = content.find("@", match.end() + 10)  # evita pegar o próprio @
        
        candidatos = [x for x in [proxima_rota, proxima_bp, proxima_decorator] if x != -1]
        fim_funcao = min(candidatos) if candidatos else len(content)
        
        bloco_funcao = content[inicio_funcao:fim_funcao]
        bloco_original = bloco_funcao
        
        # Substituições SQLite -> PostgreSQL
        bloco_funcao = bloco_funcao.replace("?", "%s")
        bloco_funcao = re.sub(r"strftime\('%Y',\s*([^)]+)\)", r"EXTRACT(YEAR FROM \1)", bloco_funcao)
        bloco_funcao = re.sub(r"strftime\('%m',\s*([^)]+)\)", r"EXTRACT(MONTH FROM \1)", bloco_funcao)
        
        if "sqlite3.connect" in bloco_funcao:
            print("   ⚠️ ATENÇÃO: A função ainda usa 'sqlite3.connect'. Verifique se a conexão está correta.")
        
        # Verifica se a função usa o helper de conexão PostgreSQL correto
        if "psycopg2" not in bloco_funcao and "get_db_connection" not in bloco_funcao and "db_postgres" not in bloco_funcao and "sqlite3.connect" not in bloco_funcao:
            print("   ℹ️ Não encontrei referência explícita a conexão de banco. Pode ser um helper global.")
        
        if bloco_funcao != bloco_original:
            content = content.replace(bloco_original, bloco_funcao)
            alterado = True
            print("   ✅ Query atualizada para padrão PostgreSQL.")
        else:
            print("   ℹ️ Nenhuma alteração de sintaxe SQLite foi necessária.")
    else:
        print("   ⚠️ Não consegui localizar a função que responde à rota (o padrão do decorator pode ser diferente).")
    
    if alterado:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✅ Arquivo salvo: {caminho_arquivo}")
    else:
        print(f"   Nenhuma alteração salva em {caminho_arquivo}")

print("\n🔎 Fim da varredura. Reinicie o backend e teste a tela de Comparativo de Receitas.")
