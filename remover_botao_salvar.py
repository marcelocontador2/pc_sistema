import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_centro_custos_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_btn_salvar_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Remove a tag <button> ou <a> que contém o texto "Salvar Relatório"
c = re.sub(r'<button[^>]*>[^<]*Salvar Relatório[^<]*</button>', '', c, flags=re.IGNORECASE)
c = re.sub(r'<a[^>]*>[^<]*Salvar Relatório[^<]*</a>', '', c, flags=re.IGNORECASE)

# 2. Remove o ícone de disquete (emoji) caso ele tenha ficado solto no HTML
c = c.replace('💾', '')

# 3. Adiciona uma regra no CSS de impressão para esconder QUALQUER botão que sobre
if '@media print' in c:
    # Injeta a regra logo no início do bloco @media print existente
    c = c.replace('@media print {', '@media print {\n            button, .btn, .no-print { display: none !important; }')
else:
    # Se não houver bloco de impressão, cria um
    css = """
    <style>
        @media print {
            button, .btn, .no-print { display: none !important; }
        }
    </style>
    """
    c = c.replace('</head>', css + '\n</head>', 1)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Salvar Relatório' removido e regra de impressão aplicada!")
