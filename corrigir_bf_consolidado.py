import re, shutil, datetime

arq_main = r"pc_backend\main.py"
shutil.copy2(arq_main, f"pc_backend\\main_backup_bf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

with open(arq_main, "r", encoding="utf-8") as f:
    main_code = f.read()

# Localiza o bloco da API de relatório consolidado
padrao_api = re.compile(
    r'(async def api_relatorio_consolidado_novo\(periodo: str\):.*?)(?=\n@app\.|\Z)',
    re.DOTALL
)

match = padrao_api.search(main_code)
if not match:
    print("[ERRO] Função api_relatorio_consolidado_novo não encontrada no main.py.")
    exit()

bloco_antigo = match.group(1)

# Nova versão da função (com a regra especial para BF)
nova_funcao = '''async def api_relatorio_consolidado_novo(periodo: str):
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
            # Regra especial para BF (que grava o período concatenado com " vs ")
            if chave == "analise_financeira_bf":
                cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE periodo LIKE ? ORDER BY id DESC LIMIT 1", (f"%{periodo}%",))
            else:
                # Busca exata com TRIM/UPPER para todos os outros
                cursor.execute(f"SELECT resultado_json, data_geracao FROM {tabela} WHERE TRIM(UPPER(periodo)) = TRIM(UPPER(?)) ORDER BY id DESC LIMIT 1", (periodo,))
            
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

main_code = main_code.replace(bloco_antigo, nova_funcao)

with open(arq_main, "w", encoding="utf-8") as f:
    f.write(main_code)

print("[OK] Função api_relatorio_consolidado_novo atualizada com a regra especial para o BF.")
print("\n=== PROXIMO PASSO ===")
print("1. REINICIE o servidor uvicorn.")
print("2. Aperte Ctrl+Shift+R no navegador.")
print("3. Clique em Verificar Dados novamente.")
