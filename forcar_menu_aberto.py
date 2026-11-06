import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_menu_aberto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Procura o script que monta o menu dinâmico e força a exibição
# O script original tem algo como: linkPai.addEventListener('click', function() { ... })
# Vamos injetar uma instrução que força o submenu a ficar visível logo após ele ser criado.

# Procura o momento em que o submenu é adicionado ao DOM
idx_append = html.find("submenu.appendChild")
if idx_append != -1:
    # Encontra o final dessa linha/expressão
    end_append = html.find(";", idx_append)
    if end_append == -1:
        end_append = idx_append + 50
    
    # Adiciona um style para garantir que ele fique aberto, logo após o append
    injecao = """
    // --- FORÇAR SUBMENU ABERTO ---
    if (submenu) {
        submenu.style.display = 'block';
        submenu.style.listStyle = 'none';
        submenu.style.paddingLeft = '15px';
        submenu.style.margin = '0';
    }
    // -----------------------------
"""
    # Procura a próxima linha em branco ou o fechamento do bloco para injetar
    html = html[:end_append+1] + injecao + html[end_append+1:]
    print("[OK] Instrução de 'submenu sempre aberto' injetada via JavaScript.")

# 2. Caso o menu seja renderizado no HTML estático (o que é mais provável após os scripts anteriores)
# Vamos adicionar uma regra CSS global que força a exibição de qualquer submenu
css_forcar = """
<style>
    /* Força o submenu de Análises Contábeis a ficar sempre visível */
    #submenu-analises, .submenu {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
        max-height: none !important;
    }
    /* Remove a seta ou indicador de 'fechado' se houver */
    #menu-analises::after {
        content: " ▼" !important;
    }
</style>
"""
# Insere o CSS antes do </head>
idx_head = html.find("</head>")
if idx_head != -1:
    html = html[:idx_head] + css_forcar + html[idx_head:]
    print("[OK] Regra CSS de 'submenu aberto' injetada.")

# 3. Salvar
with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PROXIMO PASSO ===")
print("1. Va no navegador e aperte Ctrl+Shift+R.")
print("2. O menu 'Análises Contábeis' deve estar aberto, com todos os itens visíveis.")
