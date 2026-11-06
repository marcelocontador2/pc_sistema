with open("pc_frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mostra todos os <a href> do menu
print("=== LINKS DO MENU (href) ===")
import re
for m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.IGNORECASE):
    href = m.group(1)
    texto = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    if href and ('analise' in href or 'conferencia' in href or 'config' in href or 'base_legal' in href):
        print(f"  {href} -> {texto}")

# 2. Mostra o trecho em volta de "Conferência" para vermos a estrutura
print("\n=== TRECHO EM VOLTA DE 'Conferência das Demonstrações' ===")
idx = html.find('Conferência das Demonstrações')
if idx != -1:
    # Volta até o '<li' ou '<a' mais próximo
    inicio = max(0, idx - 300)
    fim = min(len(html), idx + 300)
    print(html[inicio:fim])
else:
    print("Não encontrei 'Conferência das Demonstrações'.")

# 3. Mostra o trecho em volta de "Configurações"
print("\n=== TRECHO EM VOLTA DE 'Configurações' ===")
idx2 = html.find('>Configurações<')
if idx2 != -1:
    inicio2 = max(0, idx2 - 200)
    fim2 = min(len(html), idx2 + 200)
    print(html[inicio2:fim2])
else:
    print("Não encontrei 'Configurações' no menu.")

# 4. Mostra as últimas 20 linhas do arquivo
print("\n=== ULTIMAS 20 LINHAS DO ARQUIVO ===")
linhas = html.split("\n")
for l in linhas[-20:]:
    print(l)
