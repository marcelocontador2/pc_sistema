import os
import re
import shutil

# Procura o backup de 11/11/2026 (ou qualquer backup que tenha o template HTML grande)
arquivo_backup = None
for root, dirs, files in os.walk("."):
    if "pc_venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.startswith("main.py.bak") or file.startswith("main.py.bak_"):
            caminho = os.path.join(root, file)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    # Procura por um bloco HTML grande (mais de 5000 caracteres) dentro da função de PDF
                    if "gerar_pdf_relatorio_consolidado" in conteudo:
                        # Extrai a função
                        idx_inicio = conteudo.find("def gerar_pdf_relatorio_consolidado(")
                        if idx_inicio != -1:
                            idx_fim = conteudo.find("\n@app.", idx_inicio)
                            if idx_fim == -1:
                                idx_fim = len(conteudo)
                            funcao = conteudo[idx_inicio:idx_fim]
                            
                            # Verifica se há HTML grande (template)
                            html_matches = re.findall(r'html_parts\.append\([^)]*\)', funcao)
                            if len(html_matches) > 50:  # Muitas partes de HTML = template completo
                                arquivo_backup = caminho
                                print(f"✅ Backup com template encontrado: {caminho}")
                                print(f"   Tamanho da função: {len(funcao)} caracteres")
                                print(f"   Partes de HTML: {len(html_matches)}")
                                break
            except:
                pass
    if arquivo_backup:
        break

if not arquivo_backup:
    print("❌ Nenhum backup com template HTML grande foi encontrado.")
    print("   Vou tentar extrair o template do PDF de referência (relatorio_consolidado_29).")
else:
    # Salva a função em um arquivo separado para análise
    with open("funcao_template_original.py", "w", encoding="utf-8") as f:
        f.write(funcao)
    print(f"\n✅ Função salva em: funcao_template_original.py")
    print(f"   Tamanho: {len(funcao)} caracteres")
