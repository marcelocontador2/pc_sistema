arq = r"pc_backend\main.py"
with open(arq, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substitui o bloco de largura de colunas e cabeçalho
bloco_cabecalho_antigo = """    col_w = [70, 40, 40, 30]
    headers = ["Conta", "Periodo Atual (R$)", "Periodo Anterior (R$)", "Var. (%)"]"""

bloco_cabecalho_novo = """    col_w = [55, 35, 35, 25, 25]
    headers = ["Conta", "Periodo Atual (R$)", "Periodo Anterior (R$)", "Var. (%)", "AV (%)"]"""

html = html.replace(bloco_cabecalho_antigo, bloco_cabecalho_novo)

# 2. Substitui a função linha
bloco_linha_antigo = """    def linha(label, va, vb):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        pdf.ln()"""

bloco_linha_novo = """    def linha(label, va, vb, base_av=0):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")
        
        # Variação (%)
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        
        # Análise Vertical (AV %)
        if base_av and base_av != 0:
            av = (va / base_av) * 100
            av_str = f"{av:,.2f}%".replace(".", ",")
        else:
            av_str = "-"
        pdf.cell(col_w[4], 7, av_str, border=1, align="R")
        
        pdf.ln()"""

html = html.replace(bloco_linha_antigo, bloco_linha_novo)

# 3. Substitui o bloco de chamadas da função linha para incluir o Total do Ativo/Passivo
bloco_chamadas_antigo = """    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0))
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0))
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0))
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0))
    linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0))
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0))
    linha("TOTAL DO ATIVO", d.get("total_ativo", {}).get("atual", 0), d.get("total_ativo", {}).get("anterior", 0))
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0))
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0))
    linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0))
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0))
    linha("TOTAL DO PASSIVO", d.get("total_passivo", {}).get("atual", 0), d.get("total_passivo", {}).get("anterior", 0))
    linha("SuperÃ¡vit Financeiro", 63825301.60, 114355899.33)"""

bloco_chamadas_novo = """    tot_ativo = d.get("total_ativo", {}).get("atual", 0)
    tot_passivo = d.get("total_passivo", {}).get("atual", 0)

    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0), tot_ativo)
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0), tot_ativo)
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0), tot_ativo)
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0), tot_ativo)
    linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0), tot_ativo)
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0), tot_ativo)
    linha("TOTAL DO ATIVO", tot_ativo, d.get("total_ativo", {}).get("anterior", 0), tot_ativo)
    
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0), tot_passivo)
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0), tot_passivo)
    linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0), tot_passivo)
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0), tot_passivo)
    linha("TOTAL DO PASSIVO", tot_passivo, d.get("total_passivo", {}).get("anterior", 0), tot_passivo)
    
    linha("Superavit Financeiro", 63825301.60, 114355899.33, tot_ativo)"""

html = html.replace(bloco_chamadas_antigo, bloco_chamadas_novo)

with open(arq, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Coluna AV (%) adicionada com sucesso ao gerador de PDF do backend!")
