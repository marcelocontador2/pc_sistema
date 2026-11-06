import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/liquidez.html"
shutil.copy2(arq, f"{arq}.bak_voltar_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Substitui o link por um botao que funciona
antigo = '<a href="/" class="btn-voltar-laranja btn btn-azul">&#8592; Voltar</a>'
novo = '<button class="btn-voltar-laranja" onclick="window.location.href='/'">&#8592; Voltar</button>'

if antigo in c:
    c = c.replace(antigo, novo)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Botao 'Voltar' substituido por <button> funcional.")
else:
    # Tenta encontrar qualquer <a> com "Voltar" e class="btn-voltar-laranja"
    import re
    padrao = re.compile(r'<a[^>]*class="[^"]*btn-voltar-laranja[^"]*"[^>]*>.*?Voltar.*?</a>', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(0), novo)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Botao 'Voltar' corrigido via regex.")
    else:
        print("[ERRO] Nao foi possivel encontrar o botao 'Voltar'.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
