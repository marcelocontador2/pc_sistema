import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# =====================================================================
# PATCH 1: Corrige os nomes no mapa_tabelas e ordem_modelo (tira o mojibake)
# =====================================================================
correcoes = {
    "An횄징lise BP": "Análise BP",
    "An횄징lise Or횄짠ament횄징ria (BO)": "Análise Orçamentária (BO)",
    "An횄징lise Financeira (BF)": "Análise Financeira (BF)",
    "An횄징lise DFC": "Análise DFC",
    "An횄징lise Patrimonial (DVP)": "Análise Patrimonial (DVP)",
    "Demonstra횄짠횄짙o das Muta횄짠횄쨉es do PL (DMPL)": "Demonstração das Mutações do PL (DMPL)",
    "DMPL": "Demonstração das Mutações do PL (DMPL)",
    "횄횂ndices de Liquidez": "Índices de Liquidez",
    "횄ndices de Liquidez": "Índices de Liquidez",
    "Integridade entre Demonstra횄짠횄쨉es": "Integridade entre Demonstrações",
    "Confer횄짧ncia das Demonstra횄짠횄쨉es": "Conferência das Demonstrações",
    "An횄징lise por Centro de Custos": "Análise por Centro de Custos",
    "Demonstra횄짠횄짙o das Muta횄짠횄쨉es do Patrim횄쨈nio L횄횂quido (DMPL)": "Demonstração das Mutações do Patrimônio Líquido (DMPL)",
}
for errado, certo in correcoes.items():
    texto = texto.replace(errado, certo)

# =====================================================================
# PATCH 2: No bloco do DFC (linha ~7060), corrige a leitura para "operacional"
# =====================================================================
# Encontra o bloco onde ele tenta ler dados_dfc["caixa"]
padrao_dfc = re.compile(r'if "caixa" in dados_dfc:.*?</tbody></table>', re.DOTALL)
match = padrao_dfc.search(texto)

if match:
    novo_dfc = '''if "operacional" in dados_dfc or "investimento" in dados_dfc or "financiamento" in dados_dfc:
                        html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>Grupo</th><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for grupo_nome in ["operacional", "investimento", "financiamento"]:
                            grupo = dados_dfc.get(grupo_nome, {})
                            for k, v in grupo.items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    rotulo = f"{grupo_nome.capitalize()} - {k.title()}"
                                    html_parts.append(f"<tr><td>{grupo_nome.capitalize()}</td><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                    if abs(var) > 0.01:
                                        direcao = "positiva" if var > 0 else "negativa"
                                        textos.append(f"<li>{rotulo}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")'''
    texto = texto[:match.start()] + novo_dfc + texto[match.end():]
    print("[OK] Bloco do DFC corrigido para ler 'operacional'.")
else:
    print("[AVISO] Bloco do DFC (if 'caixa') nao encontrado.")

# =====================================================================
# PATCH 3: No bloco da Liquidez (linha ~7389), corrige a leitura para "liquidez"
# =====================================================================
# Encontra o bloco onde ele tenta ler liq/estrutura (o fallback 'Sem variações')
padrao_liq = re.compile(r'# ---- TEXTOS DINAMICOS ----.*?</tbody></table>', re.DOTALL)
match_liq = padrao_liq.search(texto)

if match_liq:
    novo_liq = '''# ---- TEXTOS DINAMICOS ----
                    liq_data = dados_item if isinstance(dados_item, dict) else {}
                    liq = liq_data.get("liquidez", {})
                    liq_ant = liq_data.get("liquidez_anterior", {})
                    est = liq_data.get("estrutura", {})
                    est_ant = liq_data.get("estrutura_anterior", {})
                    
                    html_parts.append("<h3>Índices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                    for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                    html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                    for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                    html_parts.append("</tbody></table>")'''
    texto = texto[:match_liq.start()] + novo_liq + texto[match_liq.end():]
    print("[OK] Bloco da Liquidez corrigido para ler 'liquidez'.")
else:
    print("[AVISO] Bloco da Liquidez nao encontrado.")

# =====================================================================
# PATCH 4: Corrige os acentos no título do PDF (RELATÍ“RIO -> RELATÓRIO)
# =====================================================================
texto = texto.replace("RELATÍ“RIO CONSOLIDADO", "RELATÓRIO CONSOLIDADO")
texto = texto.replace("RELATÍRIO CONSOLIDADO", "RELATÓRIO CONSOLIDADO")
texto = texto.replace("PERÍODO DE ANÁLISE", "PERÍODO DE ANÁLISE")

# =====================================================================
# PATCH 5: Corrige a leitura da API (que busca os dados)
# =====================================================================
# O bloco da api_relatorio_consolidado_novo precisa usar LIKE e ler resultado_json
if 'for chave, tabela in modulos.items():' in texto:
    # Procura a ocorrencia dentro da funcao api_relatorio_consolidado_novo
    inicio_api = texto.find('async def api_relatorio_consolidado_novo')
    if inicio_api != -1:
        # A funcao vai ate o proximo @app
        fim_api = texto.find('@app', inicio_api + 10)
        if fim_api == -1: fim_api = len(texto)
        
        bloco_api = texto[inicio_api:fim_api]
        
        # Substitui o loop antigo por um que leia resultado_json/dados_json com LIKE
        novo_loop = '''    encontrados = []
    faltando = []
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    for chave, tabela in modulos.items():
        try:
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
        # Substitui o corpo da funcao
        inicio_corpo = bloco_api.find('encontrados = []')
        if inicio_corpo != -1:
            bloco_api = bloco_api[:inicio_corpo] + novo_loop
            texto = texto[:inicio_api] + bloco_api + texto[fim_api:]
            print("[OK] Funcao da API corrigida para ler resultado_json/dados_json com LIKE.")

# Salva
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Patches aplicados. O layout original foi mantido.")
