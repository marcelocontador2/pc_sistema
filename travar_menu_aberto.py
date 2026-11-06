import shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_estatico_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Só injeta o CSS se ainda não existir
if "/* TRAVAR MENU ABERTO */" not in html:
    css_fix = """
<style>
    /* TRAVAR MENU ABERTO */
    /* Força a lista de itens do menu a ficar sempre visível */
    #submenu-analises, .submenu {
        display: block !important;
        visibility: visible !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
    }
</style>
"""
    # Insere antes do </head> para garantir que carregue primeiro
    idx_head = html.find("</head>")
    if idx_head != -1:
        html = html[:idx_head] + css_fix + html[idx_head:]
        
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] CSS injetado: O menu agora é estático e não fecha mais.")
    else:
        print("[AVISO] Não encontrei a tag </head> no arquivo.")
else:
    print("[INFO] A regra para manter o menu aberto já existe.")
