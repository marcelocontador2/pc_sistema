c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Mostra o trecho onde o menu deveria estar
idx = c.find('Importar Relatórios')
if idx != -1:
    print("=" * 70)
    print("TRECHO DO MENU (a partir de 'Importar Relatórios')")
    print("=" * 70)
    print(c[max(0, idx-500):idx+3000])
else:
    print("[ERRO] Nao encontrei 'Importar Relatórios' no HTML.")
    print("Mostrando o inicio do HTML (0-2000):")
    print(c[:2000])
