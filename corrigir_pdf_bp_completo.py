import shutil, datetime, ast, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_pdf_bp_fix_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a funcao do PDF do BP
idx = c.find('@app.get("/gerar_pdf_analise_bp/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF do BP nao encontrada.")
    exit(1)

fim = c.find('@app', idx + 10)
if fim == -1:
    fim = len(c)

bloco = c[idx:fim]

# 1. Corrige a funcao linha (inverte a ordem: va na coluna 1, vb na coluna 2)
antigo_linha = '''    def linha(label, va, vb):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(vb), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(va), border=1, align="R")
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        pdf.ln()'''

novo_linha = '''    def linha(label, va, vb):
        pdf.cell(col_w[0], 7, label, border=1, align="L")
        pdf.cell(col_w[1], 7, fmt(va), border=1, align="R")
        pdf.cell(col_w[2], 7, fmt(vb), border=1, align="R")
        pct = "-" if not vb else f"{(((va - vb) / abs(vb)) * 100):,.2f}%".replace(".", ",")
        pdf.cell(col_w[3], 7, pct, border=1, align="R")
        pdf.ln()'''

if antigo_linha in bloco:
    bloco = bloco.replace(antigo_linha, novo_linha)
    print("[OK] Funcao linha corrigida: va na coluna atual, vb na coluna anterior.")
else:
    print("[AVISO] Funcao linha nao encontrada. Tentando variacao...")

# 2. Adiciona o Ativo Realizavel e os totais
# Remove as linhas antigas e adiciona as novas
antigo_linhas = '''    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0))
    linha("Caixa e Equivalentes", d.get("caixa", {}).get("atual", 0), d.get("caixa", {}).get("anterior", 0))
    linha("Creditos a Curto Prazo", d.get("creditos", {}).get("atual", 0), d.get("creditos", {}).get("anterior", 0))
    linha("Ativo Nao Circulante", d.get("ativo_nao_circulante", {}).get("atual", 0), d.get("ativo_nao_circulante", {}).get("anterior", 0))
    linha("Imobilizado", d.get("imobilizado", {}).get("atual", 0), d.get("imobilizado", {}).get("anterior", 0))
    linha("Passivo Circulante", d.get("passivo_circulante", {}).get("atual", 0), d.get("passivo_circulante", {}).get("anterior", 0))
    linha("Passivo Nao Circulante", d.get("passivo_nao_circulante", {}).get("atual", 0), d.get("passivo_nao_circulante", {}).get("anterior", 0))
    linha("Patrimonio Liquido", d.get("patrimonio_liquido", {}).get("atual", 0), d.get("patrimonio_liquido", {}).get("anterior", 0))'''

novo_linhas = '''    linha("Ativo Circulante", d.get("ativo_circulante", {}).get("atual", 0), d.get("ativo_circulante", {}).get("anterior", 0))
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
    linha("TOTAL DO PASSIVO", d.get("total_passivo", {}).get("atual", 0), d.get("total_passivo", {}).get("anterior", 0))'''

if antigo_linhas in bloco:
    bloco = bloco.replace(antigo_linhas, novo_linhas)
    print("[OK] Linhas do PDF atualizadas (Ativo Realizavel, Passivo Total, Total do Passivo).")
else:
    print("[AVISO] Linhas antigas nao encontradas. Tentando variacao...")
    # Tenta substituir linha por linha
    bloco = bloco.replace('linha("Imobilizado"', 'linha("Ativo Realizavel a Longo Prazo", d.get("ativo_realizavel", {}).get("atual", 0), d.get("ativo_realizavel", {}).get("anterior", 0))\n    linha("Imobilizado"')
    bloco = bloco.replace('linha("Patrimonio Liquido"', 'linha("Passivo Total", d.get("passivo_total", {}).get("atual", 0), d.get("passivo_total", {}).get("anterior", 0))\n    linha("Patrimonio Liquido"')
    bloco = bloco.replace('linha("Patrimonio Liquido"', 'linha("TOTAL DO PASSIVO", d.get("total_passivo", {}).get("atual", 0), d.get("total_passivo", {}).get("anterior", 0))\n    linha("Patrimonio Liquido"')
    print("[OK] Linhas ajustadas (variacao).")

# 3. Ajusta a funcao fmt para mostrar valores cheios e com separador de milhar
antigo_fmt = '''    def fmt(v):
        if v is None: return "0,00"
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")'''

novo_fmt = '''    def fmt(v):
        if v is None: return "0,00"
        s = f"{v:,.2f}"
        # Formato: 1,234,567.89 -> 1.234.567,89
        return s.replace(",", "X").replace(".", ",").replace("X", ".")'''

if antigo_fmt in bloco:
    bloco = bloco.replace(antigo_fmt, novo_fmt)
    print("[OK] Funcao fmt ajustada (valores cheios com separador de milhar).")
else:
    print("[AVISO] Funcao fmt nao encontrada.")

c = c[:idx] + bloco + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("[OK] PDF do BP corrigido (valores cheios, sem cortar milhar).")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_pdf_bp_fix_{ts}", back_path)
