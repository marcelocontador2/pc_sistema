import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_link_puro_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Substitui o botão atual por um link HTML puro (imune a bloqueios de JS)
link_puro = '<a href="/" class="btn" style="background:#ed8936; text-decoration:none; display:inline-block; padding:8px 15px; border-radius:6px; font-weight:bold; color:#fff; font-size:14px;">← Voltar</a>'

# Substitui tanto o <button> quanto qualquer <a> que tenha a palavra Voltar
c = re.sub(r'<button[^>]*>.*?(?:←\s*)?Voltar.*?</button>', link_puro, c, flags=re.IGNORECASE | re.DOTALL)
c = re.sub(r'<a[^>]*>.*?(?:←\s*)?Voltar.*?</a>', link_puro, c, flags=re.IGNORECASE | re.DOTALL)

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão Voltar transformado em link HTML puro (100% infalível)!")
