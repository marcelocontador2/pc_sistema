p = 'pc_frontend/index.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Adicionar no menu lateral (sidebar)
old_menu = '<li><a href="/notas_explicativas" style="display:block; padding:10px 0px; text-decoration:none; color:#333;">📝 Notas Explicativas</a></li>'
new_menu = old_menu + '\n            <li><a href="/notas_mcasp" style="display:block; padding:10px 0px; text-decoration:none; color:#333;">📘 Notas Explicativas - MCASP</a></li>'

# 2. Adicionar nos atalhos (shortcut)
old_short = '<a href="/notas_explicativas" class="shortcut-btn">📝 Notas Explicativas</a>'
new_short = old_short + '\n            <a href="/notas_mcasp" class="shortcut-btn">📘 Notas Explicativas - MCASP</a>'

if old_menu not in s:
    print('AVISO: Link do menu lateral nao encontrado exatamente como esperado. Tentando variacao.')
    # Tenta achar pela substring href
    import re
    padrao_menu = r'(<li><a href="/notas_explicativas"[^>]*>.*?</a></li>)'
    match = re.search(padrao_menu, s)
    if match:
        s = s.replace(match.group(1), match.group(1) + '\n            <li><a href="/notas_mcasp" style="display:block; padding:10px 0px; text-decoration:none; color:#333;">📘 Notas Explicativas - MCASP</a></li>', 1)
        print('OK: Menu lateral atualizado (via regex).')
    else:
        print('ERRO: Nao foi possivel encontrar o link do menu.')

if old_short in s:
    s = s.replace(old_short, new_short, 1)
    print('OK: Atalhos atualizados.')
else:
    print('AVISO: Atalho nao encontrado exatamente.')

# Salva o arquivo
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('Arquivo index.html salvo.')
