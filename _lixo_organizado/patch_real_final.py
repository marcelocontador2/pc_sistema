import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

# ---------------------------------------------------------
# PATCH 1: DFC (Achar o bloco 'elif ... DFC' e substituir o corpo)
# ---------------------------------------------------------
padrao_dfc = re.compile(
    r'(elif nome_interno == "An[aá]lise DFC":)\s*.*?(?=\n\s*elif nome_interno ==)',
    re.DOTALL
)

novo_dfc = '''elif nome_interno == "Análise DFC":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    # Pega os dados (que podem estar em 'dados')
                    dados_dfc = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) else {}
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração do Fluxo de Caixa (método direto).</p>")
                    
                    textos = []
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc and isinstance(dados_dfc[tipo], dict):
                            html_parts.append(f"<h3>Fluxo {tipo.title()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                            html_parts.append("</tbody></table>")
                    
                    # Caixa
                    if "caixa" in dados_dfc and isinstance(dados_dfc["caixa"], dict):
                        html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for k, v in dados_dfc["caixa"].items():
                            if isinstance(v, dict):
                                a = v.get("atual", 0)
                                ant = v.get("anterior", 0)
                                var = calc_var(a, ant)
                                html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                        html_parts.append("</tbody></table>")
                '''

if padrao_dfc.search(texto):
    texto = padrao_dfc.sub(novo_dfc, texto, count=1)
    print("[OK] Patch 1: Bloco do DFC substituído.")
else:
    print("[ERRO] Patch 1: Não encontrei o bloco do DFC.")

# ---------------------------------------------------------
# PATCH 2: LIQUIDEZ (Substituir o bloco inteiro)
# ---------------------------------------------------------
padrao_liq = re.compile(
    r'(elif nome_interno == "[^"]*ndices de Liquidez":)\s*.*?(?=\n\s*elif nome_interno ==|\n\s*else:)',
    re.DOTALL
)

novo_liq = '''elif nome_interno == "Índices de Liquidez":
                    base = mod_dados.get("dados", mod_dados) if isinstance(mod_dados, dict) else {}
                    liq = base.get("liquidez", {})
                    liq_ant = base.get("liquidez_anterior", {})
                    est = base.get("estrutura", {})
                    est_ant = base.get("estrutura_anterior", {})
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Indicadores de liquidez e estrutura patrimonial.</p>")
                    
                    html_parts.append("<h3>Índices de Liquidez</h3><table><thead><tr><th>Indicador</th><th>Atual</th><th>Anterior</th></tr></thead><tbody>")
                    for k in ["liquidez_imediata", "liquidez_corrente", "liquidez_seca", "liquidez_geral"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{liq.get(k, '-')}</td><td>{liq_ant.get(k, '-')}</td></tr>")
                    html_parts.append("<tr><th colspan='3' style='background:#e3f2fd'>ESTRUTURA</th></tr>")
                    for k in ["endividamento_geral", "part_capital_terceiros", "imobilizacao_pl"]:
                        html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td>{est.get(k, '-')}</td><td>{est_ant.get(k, '-')}</td></tr>")
                    html_parts.append("</tbody></table>")
                '''

if padrao_liq.search(texto):
    texto = padrao_liq.sub(novo_liq, texto, count=1)
    print("[OK] Patch 2: Bloco da Liquidez substituído.")
else:
    print("[ERRO] Patch 2: Não encontrei o bloco da Liquidez.")

# Salvar
arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
