import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_sem_alerta_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Força o botão Voltar a ser um link direto e limpo, sem onclick e sem eventos
# Procura qualquer coisa que tenha "Voltar" (seja <a> ou <button>) e substitui por um link puro
c = re.sub(
    r'<(?:a|button)[^>]*>.*?Voltar.*?</(?:a|button)>',
    '<a href="/" class="btn" style="background:#ed8936; text-decoration:none;">&#8592; Voltar</a>',
    c, flags=re.IGNORECASE | re.DOTALL
)

# 2. Caça todos os alertas de "Marque um relatório" e remove, deixando apenas o return
c = re.sub(
    r'alert\("Atenção: Marque um relatório no histórico antes de gerar o PDF\."\);\s*',
    '',
    c
)
c = re.sub(
    r'alert\(\'Atenção: Marque um relatório no histórico antes de gerar o PDF\.\'\);\s*',
    '',
    c
)

# 3. Caso exista alguma função atrelada ao botão voltar, vamos garantir que o href puro resolva.
# Remove qualquer addEventListener que esteja capturando cliques em botões genéricos
c = re.sub(r'document\.querySelectorAll\(\'button\'\)\.forEach.*?\}\);', '', c, flags=re.DOTALL)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão Voltar transformado em link direto e alerta removido!")
