from fpdf import FPDF
import os

fonte = "C:/Windows/Fonts/arial.ttf"
print(f"Fonte existe? {os.path.exists(fonte)}")

pdf = FPDF()
pdf.add_page()
pdf.add_font("ArialUnicode", "", fonte, uni=True)
pdf.add_font("ArialUnicode", "B", fonte, uni=True)
pdf.add_font("ArialUnicode", "I", fonte, uni=True)

# Teste com acentos
pdf.set_font("ArialUnicode", "B", 16)
pdf.cell(0, 10, "TESTE: ANÁLISE DA DEMONSTRAÇÃO DO FLUXO DE CAIXA", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "", 12)
pdf.cell(0, 10, "Período: 2026-TRIMESTRE-3 | Operações | Geração Líquida", new_x="LMARGIN", new_y="NEXT")

pdf_bytes = bytes(pdf.output())
with open("teste_fpdf_utf8.pdf", "wb") as f:
    f.write(pdf_bytes)

print("[OK] PDF de teste gerado: teste_fpdf_utf8.pdf")
print("[INFO] Abra o PDF e verifique se os acentos aparecem.")
