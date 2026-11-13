import ast
import subprocess
import time
import urllib.request

print("="*70)
print("🔍 DIAGNÓSTICO FINAL DO PDF CONSOLIDADO")
print("="*70)

# 1. Verificar a função no main.py
print("\n[1/3] Verificando a função no main.py...")
with open("pc_backend/main.py", "r", encoding="utf-8") as f:
    conteudo = f.read()

idx = conteudo.find("def gerar_pdf_relatorio_consolidado(")
if idx != -1:
    # Mostra as primeiras 30 linhas da função
    bloco = conteudo[idx:idx+2000]
    print("✅ Função encontrada. Primeiras linhas:")
    for linha in bloco.split("\n")[:25]:
        print(f"   {linha.strip()}")
    
    # Verifica se a correção do bytearray está lá
    if "bytes(pdf.output(dest='S'))" in bloco:
        print("\n✅ A correção do bytearray ESTÁ na função.")
    elif "pdf.output(dest='S').encode" in bloco:
        print("\n❌ A correção do bytearray NÃO está na função (ainda tem .encode).")
    else:
        print("\n⚠️ Não encontrei a linha de output. Pode estar em outro formato.")
else:
    print("❌ Função 'gerar_pdf_relatorio_consolidado' NÃO ENCONTRADA.")

# 2. Testar a rota diretamente
print("\n[2/3] Iniciando servidor temporário para testar a rota do PDF...")
process = subprocess.Popen(
    [r".\pc_venv\Scripts\uvicorn.exe", "pc_backend.main:app", "--host", "127.0.0.1", "--port", "9998"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(6)

print("\n[3/3] Testando rota /gerar_pdf_relatorio_consolidado/25...")
try:
    req = urllib.request.Request("http://127.0.0.1:9998/gerar_pdf_relatorio_consolidado/25")
    with urllib.request.urlopen(req, timeout=15) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
        print(f"   Status HTTP: {response.status}")
        print(f"   Content-Type: {content_type}")
        print(f"   Tamanho da resposta: {len(data)} bytes")
        
        if "application/pdf" in content_type:
            print("\n✅ PDF gerado com sucesso! O arquivo tem conteúdo de PDF.")
        else:
            print(f"\n⚠️ A resposta não é um PDF. Conteúdo: {data[:300]}")
except urllib.error.HTTPError as e:
    print(f"   ❌ ERRO HTTP {e.code}: {e.reason}")
    corpo = e.read().decode("utf-8", errors="replace")
    print(f"   Corpo do erro: {corpo[:1000]}")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

process.terminate()
process.wait()

print("\n" + "="*70)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("="*70)
