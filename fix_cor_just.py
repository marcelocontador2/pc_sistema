import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_cor_botao_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Ajusta o css que ficou verde (muda a cor do texto para branco e adiciona borda)
antigo = 'btn.style.backgroundColor = "#28a745";'
novo = 'btn.style.backgroundColor = "#28a745"; btn.style.color = "white"; btn.style.padding = "2px 5px"; btn.style.borderRadius = "4px";'

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Estilo do botao justificado ajustado (numero continua visivel).")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
