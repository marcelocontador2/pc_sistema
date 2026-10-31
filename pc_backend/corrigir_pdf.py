import re

c = open('main.py', encoding='utf-8-sig').read()

# Corrige a linha do page.evaluate + page.pdf na função gerar_pdf_custo_pessoal
c = c.replace(
    'pdf_bytes = page.evaluate(\'window.dispatchEvent(new Event("load"));\'); page.pdf(format="A4", print_background=True)',
    'page.evaluate(\'window.dispatchEvent(new Event("load"));\')\n            pdf_bytes = page.pdf(format="A4", print_background=True)'
)

# Corrige a linha do page.evaluate + page.pdf na função gerar_pdf_completo_custo_pessoal (se existir)
c = c.replace(
    'pdf_bytes = page.evaluate(\'window.dispatchEvent(new Event("load"));\'); page.pdf(format="A4", print_background=True)',
    'page.evaluate(\'window.dispatchEvent(new Event("load"));\')\n            pdf_bytes = page.pdf(format="A4", print_background=True)'
)

open('main.py', 'w', encoding='utf-8').write(c)
print('[OK] main.py corrigido!')
