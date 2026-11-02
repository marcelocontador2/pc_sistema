c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Procura o link do Dashboard de várias formas possíveis
if 'id="menu-dashboard"' not in c:
    # Tenta encontrar o link pelo texto "Dashboard"
    import re
    # Substitui qualquer <a> que contenha onclick="mostrarTela('dashboard')" para adicionar o id
    c = re.sub(
        r'<a href="#" onclick="mostrarTela\(\'dashboard\'\)"',
        '<a href="#" id="menu-dashboard" onclick="mostrarTela(\'dashboard\')"',
        c
    )
    # Se não encontrou, tenta com "Início" ou "Home"
    if 'id="menu-dashboard"' not in c:
        c = re.sub(
            r'<a href="#" onclick="mostrarTela\(\'dashboard\'\)"',
            '<a href="#" id="menu-dashboard" onclick="mostrarTela(\'dashboard\')"',
            c,
            count=1
        )
    print("[OK] id='menu-dashboard' adicionado.")
else:
    print("[AVISO] id='menu-dashboard' já existe.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado!")
