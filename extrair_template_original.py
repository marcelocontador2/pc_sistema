import os
import re
import shutil

print("="*70)
print("🔍 LOCALIZANDO BACKUP DE 11/11/2026")
print("="*70)

# Procura o arquivo de backup com a data de 11/11
arquivo_backup = None
for root, dirs, files in os.walk("."):
    if "pc_venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.startswith("main.py") and ("11-11" in file or "20261111" in file or "2026-11-11" in file):
            arquivo_backup = os.path.join(root, file)
            print(f"✅ Encontrado: {arquivo_backup}")
            break
    if arquivo_backup:
        break

# Se não encontrou pelo nome, procura pelo conteúdo (função gerar_pdf_relatorio_consolidado com template HTML)
if not arquivo_backup:
    print("⚠️ Backup não encontrado pelo nome. Procurando pelo conteúdo...")
    for root, dirs, files in os.walk("."):
        if "pc_venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.startswith("main.py.bak") or file.startswith("main.py.bak_"):
                caminho = os.path.join(root, file)
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo = f.read()
                        # Procura por um bloco HTML grande dentro da função de PDF
                        if "gerar_pdf_relatorio_consolidado" in conteudo and "<html>" in conteudo and "RELATÓRIO CONSOLIDADO" in conteudo:
                            arquivo_backup = caminho
                            print(f"✅ Encontrado pelo conteúdo: {arquivo_backup}")
                            break
                except:
                    pass
        if arquivo_backup:
            break

if arquivo_backup:
    # Extrai a função de PDF desse backup
    with open(arquivo_backup, "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    # Encontra a função gerar_pdf_relatorio_consolidado
    idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
    if idx_inicio != -1:
        # Encontra o final da função
        idx_fim = conteudo.find("\n@app.", idx_inicio)
        if idx_fim == -1:
            idx_fim = len(conteudo)
        
        funcao_original = conteudo[idx_inicio:idx_fim]
        
        # Salva a função original em um arquivo separado
        with open("funcao_pdf_original_11_11.py", "w", encoding="utf-8") as f:
            f.write(funcao_original)
        
        print(f"\n✅ Função original extraída e salva em: funcao_pdf_original_11_11.py")
        print(f"   Tamanho: {len(funcao_original)} caracteres")
        
        # Mostra as primeiras 50 linhas da função para você ver
        print("\n📄 Primeiras 50 linhas da função original:")
        print("-" * 70)
        for linha in funcao_original.split("\n")[:50]:
            print(linha)
        print("-" * 70)
    else:
        print("❌ Função 'gerar_pdf_relatorio_consolidado' não encontrada no backup.")
else:
    print("❌ Nenhum backup com o template original foi encontrado.")
