import subprocess
import os
import shutil

print("="*70)
print("📄 EXTRAINDO TEMPLATE DO COMMIT b5246ef (10/11/2026)")
print("="*70)

# Cria pasta temporária
pasta_temp = "template_original_1011"
if os.path.exists(pasta_temp):
    shutil.rmtree(pasta_temp)
os.makedirs(pasta_temp)

# 1. Extrai o main.py do commit b5246ef
print("\n📌 Extraindo main.py...")
resultado = subprocess.run(
    ["git", "show", "b5246ef:pc_backend/main.py"],
    capture_output=True, text=True, encoding="utf-8"
)
if resultado.returncode == 0:
    with open(f"{pasta_temp}/main.py", "w", encoding="utf-8") as f:
        f.write(resultado.stdout)
    print(f"✅ main.py extraído: {len(resultado.stdout)} caracteres")
else:
    print(f"❌ Erro: {resultado.stderr}")

# 2. Extrai o relatorio_consolidado.html
print("\n📌 Extraindo relatorio_consolidado.html...")
resultado = subprocess.run(
    ["git", "show", "b5246ef:pc_frontend/relatorio_consolidado.html"],
    capture_output=True, text=True, encoding="utf-8"
)
if resultado.returncode == 0:
    with open(f"{pasta_temp}/relatorio_consolidado.html", "w", encoding="utf-8") as f:
        f.write(resultado.stdout)
    print(f"✅ relatorio_consolidado.html extraído: {len(resultado.stdout)} caracteres")
else:
    print(f"❌ Erro: {resultado.stderr}")

# 3. Procura a função de PDF no main.py extraído
print("\n📌 Analisando a função de PDF no main.py do commit b5246ef...")
if os.path.exists(f"{pasta_temp}/main.py"):
    with open(f"{pasta_temp}/main.py", "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    idx = conteudo.find("def gerar_pdf_relatorio_consolidado(")
    if idx != -1:
        fim = conteudo.find("\n@app.", idx)
        if fim == -1:
            fim = len(conteudo)
        funcao = conteudo[idx:fim]
        print(f"✅ Função encontrada: {len(funcao)} caracteres")
        
        # Salva a função
        with open(f"{pasta_temp}/funcao_pdf_original.py", "w", encoding="utf-8") as f:
            f.write(funcao)
        print(f"✅ Função salva em: {pasta_temp}/funcao_pdf_original.py")
        
        # Mostra as primeiras 60 linhas
        print("\n📄 Primeiras 60 linhas da função original:")
        print("-" * 70)
        for linha in funcao.split("\n")[:60]:
            print(linha[:200])
    else:
        print("❌ Função de PDF não encontrada.")

print("\n" + "="*70)
print("✅ Extração concluída! Verifique a pasta 'template_original_1011'.")
print("="*70)
