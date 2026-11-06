c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("AUDITORIA DO MENU (do logo ate o fim do menu)")
print("=" * 70)

idx = c.find('logo-area')
if idx == -1:
    idx = c.find('Importar Relatórios')

if idx != -1:
    # Acha o fim do menu (aside ou proximo script)
    fim = c.find('</aside>', idx)
    if fim == -1:
        fim = c.find('<main', idx)
    if fim == -1:
        fim = idx + 3500
    
    print(c[max(0, idx-50):fim])
else:
    print("[ERRO] Nao encontrei o menu.")
