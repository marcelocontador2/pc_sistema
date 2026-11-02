c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# 1. Adiciona o id="menu-upload" no link "Importar Relatórios" do menu
if 'id="menu-upload"' not in c:
    c = c.replace(
        '<a href="#" onclick="mostrarTela(\'upload\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar Relatórios</a>',
        '<a href="#" id="menu-upload" onclick="mostrarTela(\'upload\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar Relatórios</a>'
    )
    # Tenta variação com "Importar RelatÃ³rios" (encoding quebrado)
    c = c.replace(
        '<a href="#" onclick="mostrarTela(\'upload\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar RelatÃ³rios</a>',
        '<a href="#" id="menu-upload" onclick="mostrarTela(\'upload\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Importar RelatÃ³rios</a>'
    )
    print("[OK] id='menu-upload' adicionado.")

# 2. Adiciona o id="menu-dashboard" no link do Dashboard
if 'id="menu-dashboard"' not in c:
    c = c.replace(
        '<a href="#" onclick="mostrarTela(\'dashboard\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Dashboard</a>',
        '<a href="#" id="menu-dashboard" onclick="mostrarTela(\'dashboard\')" style="display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;">Dashboard</a>'
    )
    print("[OK] id='menu-dashboard' adicionado.")

# 3. Adiciona a div id="msg-upload" dentro do formulário de upload (ou logo após ele)
if 'id="msg-upload"' not in c:
    # Procura o fechamento do formulário
    c = c.replace(
        '</form>',
        '</form>\n            <div id="msg-upload" style="margin-top: 15px;"></div>',
        1  # Substitui apenas o primeiro </form> encontrado
    )
    print("[OK] div id='msg-upload' adicionada.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] IDs faltantes adicionados ao HTML!")
