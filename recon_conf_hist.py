import re

c = open(r"pc_frontend\conferencia.html", encoding="utf-8-sig").read()

print("=" * 70)
print("COMO A CONFERÊNCIA LIDA COM O HISTÓRICO E O PDF")
print("=" * 70)

# 1. Onde está o botão de PDF
btn_pdf = re.search(r'.{0,150}gerar_pdf_conferencia.{0,150}', c)
if btn_pdf:
    print("\n[Botão de PDF]:")
    print(btn_pdf.group(0).strip())

# 2. Onde está o histórico
hist_match = re.search(r'.{0,150}historico.{0,150}', c, re.IGNORECASE)
if hist_match:
    print("\n[Trecho do Histórico]:")
    print(hist_match.group(0).strip())
