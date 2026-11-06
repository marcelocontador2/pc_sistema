with open("pc_frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mostra o trecho em volta do texto "Importar Relatórios"
print("=== TRECHO EM VOLTA DE 'Importar Relatórios' ===")
idx = html.find('Importar Relatórios')
if idx != -1:
    inicio = max(0, idx - 500)
    fim = min(len(html), idx + 500)
    print(html[inicio:fim])
else:
    print("Não encontrado.")

print("\n=== TRECHO EM VOLTA DE 'Configurações' ===")
idx2 = html.find('>Configurações<')
if idx2 != -1:
    inicio2 = max(0, idx2 - 300)
    fim2 = min(len(html), idx2 + 300)
    print(html[inicio2:fim2])
else:
    print("Não encontrado.")

print("\n=== TRECHO EM VOLTA DE 'Análises Contábeis' ===")
idx3 = html.find('Análises Contábeis')
if idx3 != -1:
    inicio3 = max(0, idx3 - 200)
    fim3 = min(len(html), idx3 + 200)
    print(html[inicio3:fim3])
else:
    print("Não encontrado.")
