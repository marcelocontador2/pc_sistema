import re, shutil, datetime, os

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_consolidado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
print(f"[OK] Backup do main.py criado.\n")

with open(arq_main, "r", encoding="utf-8") as f:
    codigo = f.read()

# =========================================================
# 1. REMOVER A FUNÇÃO api_relatorio_consolidado ANTIGA (esqueleto)
# =========================================================
padrao_antigo = re.compile(
    r'(@app\.get\("/api/relatorio_consolidado/\{periodo\}"\).*?)(?=\n@app\.|\Z)',
    re.DOTALL
)
match = padrao_antigo.search(codigo)
if match:
    codigo = codigo.replace(match.group(1), "")
    print("[OK] Função api_relatorio_consolidado antiga removida.")

# =========================================================
# 2. REMOVER A ROTA /salvar_relatorio_consolidado ANTIGA
# =========================================================
padrao_salvar_antigo = re.compile(
    r'(@app\.post\("/salvar_relatorio_consolidado/\{periodo\}"\).*?)(?=\n@app\.|\Z)',
    re.DOTALL
)
match2 = padrao_salvar_antigo.search(codigo)
if match2:
    codigo = codigo.replace(match2.group(1), "")
    print("[OK] Rota /salvar_relatorio_consolidado antiga removida.")

# =========================================================
# 3. INSERIR AS NOVAS ROTAS
# =========================================================

# Mapeamento dos módulos: chave (nome amigável) -> tabela no banco
modulos_map = {
    "analise_bp": "historico_analise_bp",
    "analise_dfc": "historico_analise_dfc",
    "analise_patrimonial": "historico_analise_patrimonial",
    "analise_orcamentaria": "historico_analise_orcamentaria",
    "analise_financeira_bf": "historico_analise_financeira_bf",
    "comparativo_receitas": "historico_comparativo_receitas",
    "comparativo_despesas": "historico_comparativo_despesas",
    "panorama": "historico_panorama",
    "liquidez": "historico_liquidez",
    "integridade": "historico_integridade_matriz",
    "conferencia": "historico_conferencia"
}

nomes_amigaveis = {
    "analise_bp": "Análise BP",
    "analise_dfc": "Análise DFC",
    "analise_patrimonial": "Análise Patrimonial (DVP)",
    "analise_orcamentaria": "Análise Orçamentária (BO)",
    "analise_financeira_bf": "Análise Financeira (BF)",
    "comparativo_receitas": "Comparativo de Receitas",
    "comparativo_despesas": "Comparativo de Despesas",
    "panorama": "Panorama de Resultados",
    "liquidez": "Índices de Liquidez",
    "integridade": "Integridade entre Demonstrações",
    "conferencia": "Conferência das Demonstrações"
}

# 3.1 Nova rota API (GET)
nova_api = '''
@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    modulos = {
        "analise_bp": "historico_analise_bp",
        "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial",
        "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf",
        "comparativo_receitas": "historico_comparativo_receitas",
        "comparativo_despesas": "historico_comparativo_despesas",
        "panorama": "historico_panorama",
        "liquidez": "historico_liquidez",
        "integridade": "historico_integridade_matriz",
        "conferencia": "historico_conferencia"
    }
    
    nomes_amigaveis = {
        "analise_bp": "Análise BP",
        "analise_dfc": "Análise DFC",
        "analise_patrimonial": "Análise Patrimonial (DVP)",
        "analise_orcamentaria": "Análise Orçamentária (BO)",
        "analise_financeira_bf": "Análise Financeira (BF)",
        "comparativo_receitas": "Comparativo de Receitas",
        "comparativo_despesas": "Comparativo de Despesas",
        "panorama": "Panorama de Resultados",
        "liquidez": "Índices de Liquidez",
        "integridade": "Integridade entre Demonstrações",
        "conferencia": "Conferência das Demonstrações"
    }
    
    encontrados = {}
    faltando = []
    
    for chave, tabela in modulos.items():
        try:
            cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            row = cursor.fetchone()
            if row:
                try:
                    dados = json.loads(row[0])
                except:
                    dados = {"raw": row[0]}
                encontrados[chave] = {
                    "nome": nomes_amigaveis[chave],
                    "data_geracao": row[1],
                    "dados": dados
                }
            else:
                faltando.append({"chave": chave, "nome": nomes_amigaveis[chave]})
        except Exception as e:
            faltando.append({"chave": chave, "nome": nomes_amigaveis[chave], "erro": str(e)})
    
    conn.close()
    
    return {
        "periodo": periodo,
        "encontrados": encontrados,
        "faltando": faltando,
        "status": "ok" if len(faltando) == 0 else "faltando",
        "total_modulos": len(modulos),
        "total_encontrados": len(encontrados),
        "total_faltando": len(faltando)
    }
'''

# 3.2 Nova rota salvar (POST)
nova_salvar = '''
@app.post("/salvar_relatorio_consolidado/{periodo}")
async def salvar_relatorio_consolidado_novo(periodo: str):
    import sqlite3, os, json
    from datetime import datetime
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS historico_relatorio_consolidado (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, resultado_json TEXT)""")
    
    # Chama a API para coletar os dados
    dados_api = await api_relatorio_consolidado_novo(periodo)
    
    if dados_api["status"] == "faltando":
        return {
            "ok": False,
            "mensagem": f"Faltam {len(dados_api['faltando'])} módulo(s) para consolidar.",
            "faltando": dados_api["faltando"]
        }
    
    dados_consolidados = {
        "periodo": periodo,
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "dados": dados_api["encontrados"]
    }
    
    cursor.execute("INSERT INTO historico_relatorio_consolidado (periodo, data_geracao, resultado_json) VALUES (?, ?, ?)",
                   (periodo, dados_consolidados["data_geracao"], json.dumps(dados_consolidados, ensure_ascii=False)))
    conn.commit()
    conn.close()
    
    return {"ok": True, "mensagem": "Relatório consolidado salvo com sucesso!", "dados": dados_consolidados}
'''

codigo += "\n" + nova_api + "\n" + nova_salvar

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(codigo)
print("[OK] Novas rotas do Relatório Consolidado inseridas no backend.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Teste via terminal: GET /api/relatorio_consolidado/2026-TRIMESTRE-3")
