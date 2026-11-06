import os, re

print("=== PROCURANDO O SCRIPT QUE MONTA O MENU ===")

# Vamos procurar nos arquivos JS e HTML por onde o menu de Análises é criado
termos = ["Conferência das Demonstrações", "Integridade entre Demonstrações"]
arquivos_alvo = []

for root, dirs, files in os.walk("."):
    # Ignora pastas pesadas
    dirs[:] = [d for d in dirs if d not in ("pc_venv", "__pycache__", ".git", "_backups_arquivo", "_arquivo_20261031", "node_modules")]
    
    for nome in files:
        if nome.endswith(".html") or nome.endswith(".js"):
            caminho = os.path.join(root, nome)
            try:
                with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                
                # Se o arquivo tem os dois termos, provavelmente é o criador do menu
                if all(t in txt for t in termos):
                    # Ignora os arquivos de backup que criamos
                    if "backup" not in nome.lower() and "index.html" not in nome:
                        arquivos_alvo.append(caminho)
            except:
                pass

print("Arquivos candidatos encontrados:")
for a in arquivos_alvo:
    print(f" - {a}")

# Vou mostrar o trecho do index.html que contém a montagem (pode ser inline)
print("\n=== TRECHO DO INDEX.HTML (onde os itens são adicionados) ===")
with open("pc_frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Procura por um array ou appendChild que contenha os itens
idx = html.find("Integridade entre Demonstrações")
if idx != -1:
    inicio = max(0, idx - 1000)
    fim = min(len(html), idx + 1000)
    print(html[inicio:fim])
else:
    print("Não achei 'Integridade' diretamente no HTML.")
