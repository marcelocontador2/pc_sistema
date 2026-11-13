import re
import shutil

caminho = "pc_backend/main.py"

with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

shutil.copy(caminho, caminho + ".bak_trocar_db_config")

# Primeiro, vamos ver como é o PG_CONFIG (para conferir)
match_pg = re.search(r'PG_CONFIG\s*=\s*\{[^}]+\}', content)
if match_pg:
    print("📋 PG_CONFIG (usado pelas rotas que funcionam):")
    print(match_pg.group(0))
    print()

# Troca DB_CONFIG por PG_CONFIG na rota de histórico de despesas
# Localiza a função get_historico_comparativo_despesas
padrao = r'(def get_historico_comparativo_despesas\(\):.*?)conn = psycopg2\.connect\(\*\*DB_CONFIG\)'
match = re.search(padrao, content, re.DOTALL)
if match:
    # Substitui DB_CONFIG por PG_CONFIG
    content = content[:match.start(1)] + match.group(1).replace("DB_CONFIG", "PG_CONFIG") + content[match.end(1):]
    # Como o replace pode não pegar tudo, vamos garantir a linha exata
    content = content.replace(
        'def get_historico_comparativo_despesas():',
        'def get_historico_comparativo_despesas():'  # placeholder
    )
    # Substitui a linha específica dentro da função
    # Encontra o bloco da função e troca
    def substituir_no_bloco(texto, funcao_nome, antigo, novo):
        idx = texto.find(f"def {funcao_nome}(")
        if idx == -1:
            return texto
        # Encontra o fim da função (próxima @app ou def)
        proximo = re.search(r'\n@app\.', texto[idx+1:])
        if proximo:
            fim = idx + 1 + proximo.start()
        else:
            fim = len(texto)
        bloco = texto[idx:fim]
        bloco_novo = bloco.replace(antigo, novo)
        return texto[:idx] + bloco_novo + texto[fim:]
    
    content = substituir_no_bloco(content, "get_historico_comparativo_despesas", "**DB_CONFIG", "**PG_CONFIG")
    
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Rota de histórico de despesas agora usa PG_CONFIG (senha correta).")
else:
    print("⚠️ Rota não encontrada ou não usa DB_CONFIG.")

# Verifica se funcionou
with open(caminho, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("def get_historico_comparativo_despesas")
if idx != -1:
    print("\n📋 Como ficou a função:")
    print("-" * 80)
    for linha in content[idx:idx+400].split("\n")[:15]:
        print("   " + linha)
