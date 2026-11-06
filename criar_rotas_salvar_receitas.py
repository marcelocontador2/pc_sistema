import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_rota_salvar_final_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

print("=" * 70)
print("1. VERIFICANDO SE A ROTA DE SALVAR EXISTE")
print("=" * 70)

# Verifica se a rota POST de salvar está definida como decorator @app.post
match_rota = re.search(r'@app\.post\("/api/comparativo_receitas_v2/\{periodo_atual\}/salvar"\)', c)
if match_rota:
    print("[OK] Rota de salvar JÁ ESTÁ no arquivo como decorator.")
else:
    print("[FALTA] Rota de salvar NÃO está no arquivo. Vou criar.")

# Verifica se a função api_comparativo_receitas_v2 existe
if 'def api_comparativo_receitas_v2' in c:
    print("[OK] Função api_comparativo_receitas_v2 existe (podemos chamar)")
else:
    print("[AVISO] Função api_comparativo_receitas_v2 NÃO existe. Vou verificar se tem outra.")
    if 'def api_comparativo_receitas' in c:
        print("[INFO] Existe api_comparativo_receitas (versão antiga). Vou usar essa.")

# Verifica se a rota DELETE de excluir existe
match_delete = re.search(r'@app\.delete\("/historico_comparativo_receitas/\{id\}"\)', c)
if match_delete:
    print("[OK] Rota DELETE de excluir JÁ ESTÁ no arquivo.")
else:
    print("[FALTA] Rota DELETE não está no arquivo.")

# ==========================================
# 2. REMOVE ROTAS ANTIGAS DE SALVAR (se existirem)
# ==========================================
print("\n" + "=" * 70)
print("2. LIMPANDO ROTAS ANTIGAS")
print("=" * 70)

# Remove blocos antigos de rota de salvar
padrao_antigo = r'@app\.post\("/api/comparativo_receitas_v2/\{periodo_atual\}/salvar"\)\s*\n(?:async\s+)?def\s+\w+\([^)]*\):.*?(?=\n@app\.|\Z)'
if re.search(padrao_antigo, c, re.DOTALL):
    c = re.sub(padrao_antigo, '', c, flags=re.DOTALL)
    print("[OK] Removida rota de salvar antiga (se existia)")

padrao_antigo2 = r'@app\.post\("/salvar_comparativo_receitas/\{periodo_atual\}"\)\s*\n(?:async\s+)?def\s+\w+\([^)]*\):.*?(?=\n@app\.|\Z)'
if re.search(padrao_antigo2, c, re.DOTALL):
    c = re.sub(padrao_antigo2, '', c, flags=re.DOTALL)
    print("[OK] Removida rota de salvar antiga (formato 2)")

# Remove rotas DELETE antigas para recriar
padrao_delete = r'@app\.delete\("/historico_comparativo_receitas/\{id\}"\)\s*\n(?:async\s+)?def\s+\w+\([^)]*\):.*?(?=\n@app\.|\Z)'
if re.search(padrao_delete, c, re.DOTALL):
    c = re.sub(padrao_delete, '', c, flags=re.DOTALL)
    print("[OK] Removida rota DELETE antiga (vou recriar)")

# ==========================================
# 3. ADICIONA AS ROTAS NOVAS
# ==========================================
print("\n" + "=" * 70)
print("3. ADICIONANDO ROTAS NOVAS")
print("=" * 70)

novas_rotas = '''

# ============================================================
# ROTAS DE SALVAR E EXCLUIR - COMPARATIVO DE RECEITAS
# ============================================================

@app.post("/api/comparativo_receitas_v2/{periodo_atual}/salvar")
def salvar_comparativo_receitas(periodo_atual: str):
    import sqlite3, os, json
    from datetime import datetime
    
    # Pega os dados atuais via API
    try:
        dados = api_comparativo_receitas_v2(periodo_atual)
    except Exception as e:
        return {"erro": True, "mensagem": f"Erro ao buscar dados: {str(e)}"}
    
    if dados.get("erro"):
        return {"erro": True, "mensagem": dados.get("mensagem", "Dados não encontrados")}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
    
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)
    
    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", 
                (periodo_atual, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}


@app.delete("/historico_comparativo_receitas/{id}")
def excluir_historico_receitas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_receitas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}

'''

c += novas_rotas

# ==========================================
# 4. VALIDA E SALVA
# ==========================================
print("\n" + "=" * 70)
print("4. VALIDANDO E SALVANDO")
print("=" * 70)

try:
    ast.parse(c)
    print("[OK] Sintaxe do main.py validada com sucesso!")
    open(back_path, 'w', encoding='utf-8').write(c)
    print("[OK] Arquivo main.py salvo")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    print("[AVISO] NÃO salvando o arquivo para não quebrar o sistema")

# Verifica se as rotas estão no arquivo final
c_final = open(back_path, encoding='utf-8').read()
if 'salvar_comparativo_receitas' in c_final:
    print("\n[CONFIRMADO] Rota POST de salvar está no arquivo")
if 'excluir_historico_receitas' in c_final:
    print("[CONFIRMADO] Rota DELETE de excluir está no arquivo")

print("\n" + "=" * 70)
print("PRÓXIMOS PASSOS")
print("=" * 70)
print("1. REINICIE o servidor (Ctrl+C e suba de novo)")
print("2. Na tela de Receitas, aperte Ctrl+F5")
print("3. Clique em Verificar e depois em Confirmar e Salvar")
print("4. O item deve aparecer no Histórico Salvo")
