import shutil, datetime, sys

ARQUIVO = r"pc_frontend\liquidez.html"
BACKUP  = f"pc_frontend\\liquidez_backup_ajuste_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(ARQUIVO, BACKUP)
print(f"[OK] Backup: {BACKUP}\n")

with open(ARQUIVO, "r", encoding="utf-8") as f:
    html = f.read()

# Atualiza os textos das formulas para deixar o calculo matematico explicito
html = html.replace(
    "`Caixa (${m(val.caixa)}) / Passivo Circulante (${m(val.passivo_circulante)})`",
    "`Caixa (${m(val.caixa)}) / Passivo Circulante (${m(val.passivo_circulante)})` <br><span style='color:#0056b3; font-weight:bold;'>Resultado em vezes (R$ por R$ 1,00 de dívida)</span>"
)

html = html.replace(
    "`Ativo Circulante (${m(val.ativo_circulante)}) / Passivo Circulante (${m(val.passivo_circulante)})`",
    "`Ativo Circulante (${m(val.ativo_circulante)}) / Passivo Circulante (${m(val.passivo_circulante)})` <br><span style='color:#0056b3; font-weight:bold;'>Resultado em vezes (R$ por R$ 1,00 de dívida)</span>"
)

html = html.replace(
    "`(Ativo Circulante (${m(val.ativo_circulante)}) - Estoques (${m(val.estoques)})) / Passivo Circulante (${m(val.passivo_circulante)})`",
    "`(Ativo Circulante (${m(val.ativo_circulante)}) - Estoques (${m(val.estoques)})) / Passivo Circulante (${m(val.passivo_circulante)})` <br><span style='color:#0056b3; font-weight:bold;'>Resultado em vezes (R$ por R$ 1,00 de dívida)</span>"
)

html = html.replace(
    "`(Ativo Circulante (${m(val.ativo_circulante)}) + Realizável (${m(val.realizavel_lp)})) / (Passivo Circulante (${m(val.passivo_circulante)}) + Não Circulante (${m(val.passivo_nao_circulante)}))`",
    "`(Ativo Circulante (${m(val.ativo_circulante)}) + Realizável (${m(val.realizavel_lp)})) / (Passivo Circulante (${m(val.passivo_circulante)}) + Não Circulante (${m(val.passivo_nao_circulante)}))` <br><span style='color:#0056b3; font-weight:bold;'>Resultado em vezes (R$ por R$ 1,00 de dívida)</span>"
)

# Ajusta as formulas de estrutura para mostrar o x100
html = html.replace(
    "`Passivo Total (${m(val.passivo_total)}) / Ativo Total (${m(val.ativo_total)})`",
    "`(Passivo Total (${m(val.passivo_total)}) / Ativo Total (${m(val.ativo_total)})) × 100`"
)

html = html.replace(
    "`Passivo Total (${m(val.passivo_total)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})`",
    "`(Passivo Total (${m(val.passivo_total)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})) × 100`"
)

html = html.replace(
    "`Ativo Permanente (${m(val.imobilizado)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})`",
    "`(Ativo Permanente (${m(val.imobilizado)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})) × 100`"
)

with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] liquidez.html atualizado.")
print("[OK] Formulas agora deixam explicito quando e vezes (liquidez) e quando e % (estrutura).")
