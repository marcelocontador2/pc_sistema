import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

inicio = texto.find('@app.get("/api/relatorio_consolidado/{periodo}")')
if inicio == -1:
    print("[ERRO] Funcao nao encontrada.")
    sys.exit(1)

fim = texto.find('\n@app', inicio + 10)
if fim == -1:
    fim = len(texto)

novo_bloco = '''@app.get("/api/relatorio_consolidado/{periodo}")
async def api_relatorio_consolidado_novo(periodo: str):
    import psycopg2
    import json
    from pc_backend.app.config import PG_CONFIG
    
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
        "integridade": "historico_integridade",
        "conferencia": "historico_conferencia",
        "custo_pessoal": "historico_custo_pessoal",
        "centro_custos": "historico_centro_custos",
        "dmpl": "historico_analise_dmpl"
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
        "conferencia": "Conferência das Demonstrações",
        "custo_pessoal": "Custo de Pessoal",
        "centro_custos": "Análise por Centro de Custos",
        "dmpl": "Demonstração das Mutações do PL (DMPL)"
    }
    
    encontrados = []
    faltando = []
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    for chave, tabela in modulos.items():
        try:
            # Tenta periodo LIKE (tolerante a espacos)
            try:
                cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                row = cursor.fetchone()
            except Exception:
                conn.rollback()
                cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo}%",))
                row = cursor.fetchone()
            
            if row:
                item = {
                    "nome": nomes_amigaveis.get(chave, chave),
                    "data_geracao": row[1] if len(row) > 1 else "Disponível",
                    "id": row[0]
                }
                if len(row) > 2 and row[2] is not None:
                    try:
                        item["dados"] = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                    except Exception:
                        item["dados"] = row[2]
                encontrados.append(item)
            else:
                faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
        except Exception:
            conn.rollback()
            faltando.append({"nome": nomes_amigaveis.get(chave, chave)})
    
    conn.close()
    
    return {
        "status": "ok" if len(faltando) == 0 else "faltando",
        "encontrados": encontrados,
        "faltando": faltando,
        "periodo": periodo,
        "total_modulos": len(modulos),
        "total_encontrados": len(encontrados),
        "total_faltando": len(faltando)
    }

'''

texto = texto[:inicio] + novo_bloco + texto[fim:]
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Funcao api_relatorio_consolidado_novo reescrita com busca tolerante.")
