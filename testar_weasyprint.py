import subprocess
import sys

print("🔍 VERIFICANDO A BIBLIOTECA WEASYPRINT...\n")

# 1. Verifica se o weasyprint está instalado
try:
    import weasyprint
    print(f"✅ WeasyPrint instalado. Versão: {weasyprint.__version__}")
except ImportError as e:
    print(f"❌ WeasyPrint NÃO está instalado: {e}")
    print("\n🔧 Tentando instalar...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "weasyprint"], capture_output=True, text=True)
    print(result.stdout[-500:] if result.stdout else "Sem saída")
    print(result.stderr[-500:] if result.stderr else "Sem erro")

# 2. Testa a geração de um PDF simples
print("\n🔍 TESTANDO A GERAÇÃO DE PDF COM WEASYPRINT...\n")
try:
    from weasyprint import HTML
    html_test = "<html><body><h1>Teste de PDF</h1><p>Este é um teste do WeasyPrint.</p></body></html>"
    pdf_bytes = HTML(string=html_test).write_pdf()
    print(f"✅ PDF gerado com sucesso! Tamanho: {len(pdf_bytes)} bytes")
except Exception as e:
    print(f"❌ ERRO ao gerar PDF com WeasyPrint: {e}")
    print("\n⚠️ Isso indica que faltam dependências do sistema (GTK, Pango, Cairo) no Windows.")
    print("Solução alternativa: usar a biblioteca 'reportlab' ou 'xhtml2pdf'.")
