import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\panorama.html"

shutil.copy2(arquivo, f"{arquivo}.bak_voltar_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Procura o botão que tem o texto "Voltar" e restaura a função dele
# A função correta é ir para a página inicial ('/')
padrao_botao_voltar = r'<button[^>]*>\s*(?:←\s*)?Voltar\s*</button>'

novo_botao_voltar = '<button class="btn" style="background:#ed8936;" onclick="window.location.href=\'/\'">← Voltar</button>'

if re.search(padrao_botao_voltar, c, flags=re.IGNORECASE):
    c = re.sub(padrao_botao_voltar, novo_botao_voltar, c, flags=re.IGNORECASE)
    open(arquivo, 'w', encoding='utf-8').write(c)
    print("[OK] Botão '← Voltar' consertado com sucesso! Ele não chama mais o PDF.")
else:
    print("[AVISO] Não encontrei o botão Voltar com o padrão exato. Tentando substituição manual...")
    # Fallback de segurança caso o HTML tenha alguma classe diferente
    c = c.replace('onclick="gerarPDF()"', 'onclick="window.location.href=\'/\'"', 1)
    open(arquivo, 'w', encoding='utf-8').write(c)
    print("[OK] Tentativa de conserto manual aplicada.")
