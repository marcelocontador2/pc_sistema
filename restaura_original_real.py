import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# 1. Corrige os acentos no titulo principal e no mapa de tabelas
correcoes_texto = {
    "RELATÍ“RIO CONSOLIDADO": "RELATÓRIO CONSOLIDADO",
    "RELATÍRIO CONSOLIDADO": "RELATÓRIO CONSOLIDADO",
    "PERÍODO DE ANÁLISE": "PERÍODO DE ANÁLISE",
    "LEGISLAÇÍFO": "LEGISLAÇÃO",
    "DEMONSTRAÇÍES": "DEMONSTRAÇÕES",
    "An횄징lise BP": "Análise BP",
    "An횄징lise DFC": "Análise DFC",
    "An횄징lise Patrimonial (DVP)": "Análise Patrimonial (DVP)",
    "An횄징lise Or횄짠ament횄징ria (BO)": "Análise Orçamentária (BO)",
    "An횄징lise Financeira (BF)": "Análise Financeira (BF)",
    "횄횂ndices de Liquidez": "Índices de Liquidez",
    "횄ndices de Liquidez": "Índices de Liquidez",
    "Demonstra횄짠횄짙o das Muta횄짠횄쨉es do PL (DMPL)": "Demonstração das Mutações do PL (DMPL)"
}
for errado, certo in correcoes_texto.items():
    texto = texto.replace(errado, certo)

# 2. Substitui o corpo da funcao api_relatorio_consolidado_novo
# para forcar a busca tolerante (TRIMESTRAL -> TRIMESTRE)
inicio_api = texto.find('async def api_relatorio_consolidado_novo(periodo: str):')
if inicio_api != -1:
    fim_api = texto.find('@app.get', inicio_api + 10)
    if fim_api == -1: fim_api = len(texto)
    novo_corpo_api = '''async def api_relatorio_consolidado_novo(periodo: str):
    import psycopg2
    import json
    from pc_backend.app.config import PG_CONFIG
    
    # Normaliza o periodo (2026-TRIMESTRAL-3 vira 2026-TRIMESTRE-3)
    periodo_normalizado = periodo.replace("TRIMESTRAL", "TRIMESTRE").replace("trimestral", "TRIMESTRE")
    if "TRIMESTRE" in periodo_normalizado.upper():
        partes = periodo_normalizado.upper().split("-")
        if len(partes) == 3:
            periodo_normalizado = f"{partes[0]}-TRIMESTRE-{partes[2]}"

    modulos = {
        "analise_bp": "historico_analise_bp", "analise_dfc": "historico_analise_dfc",
        "analise_patrimonial": "historico_analise_patrimonial", "analise_orcamentaria": "historico_analise_orcamentaria",
        "analise_financeira_bf": "historico_analise_financeira_bf", "comparativo_receitas": "historico_comparativo_receitas",
        "comparativo_despesas": "historico_comparativo_despesas", "panorama": "historico_panorama",
        "liquidez": "historico_liquidez", "integridade": "historico_integridade",
        "conferencia": "historico_conferencia", "custo_pessoal": "historico_custo_pessoal",
        "centro_custos": "historico_centro_custos", "dmpl": "historico_analise_dmpl"
    }
    nomes_amigaveis = {
        "analise_bp": "Análise BP", "analise_dfc": "Análise DFC",
        "analise_patrimonial": "Análise Patrimonial (DVP)", "analise_orcamentaria": "Análise Orçamentária (BO)",
        "analise_financeira_bf": "Análise Financeira (BF)", "comparativo_receitas": "Comparativo de Receitas",
        "comparativo_despesas": "Comparativo de Despesas", "panorama": "Panorama de Resultados",
        "liquidez": "Índices de Liquidez", "integridade": "Integridade entre Demonstrações",
        "conferencia": "Conferência das Demonstrações", "custo_pessoal": "Custo de Pessoal",
        "centro_custos": "Análise por Centro de Custos", "dmpl": "Demonstração das Mutações do PL (DMPL)"
    }
    
    encontrados = []
    faltando = []
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    for chave, tabela in modulos.items():
        try:
            try:
                cursor.execute(f"SELECT id, data_geracao, resultado_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo_normalizado}%",))
                row = cursor.fetchone()
            except Exception:
                conn.rollback()
                cursor.execute(f"SELECT id, data_geracao, dados_json FROM {tabela} WHERE periodo LIKE %s LIMIT 1", (f"%{periodo_normalizado}%",))
                row = cursor.fetchone()
            
            if row:
                item = {"nome": nomes_amigaveis.get(chave, chave), "data_geracao": row[1] if len(row) > 1 else "Disponível", "id": row[0]}
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
        "encontrados": encontrados, "faltando": faltando, "periodo": periodo,
        "total_modulos": len(modulos), "total_encontrados": len(encontrados), "total_faltando": len(faltando)
    }

'''
    texto = texto[:inicio_api] + novo_corpo_api + texto[fim_api:]

# 3. O pulo do gato: Substituir os blocos de leitura do DFC e Liquidez dentro do template original
# O template original procura por 'caixa' no DFC, mas o banco manda 'operacional'
texto = texto.replace('if "caixa" in dados_dfc:', 'if "operacional" in dados_dfc:')
texto = texto.replace('for k, v in dados_dfc["caixa"].items():', 'for k, v in dados_dfc.get("operacional", {}).items():')
texto = texto.replace('dados_dfc["caixa"]', 'dados_dfc.get("operacional", {})')

# 4. Salva o arquivo
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Codigo original restaurado e patches aplicados!")
