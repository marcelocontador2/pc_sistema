import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_salvar_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# A função salvarMatriz atual
antigo = '''            await fetch("/salvar_integridade_matriz/" + periodo, { method: 'POST' });'''

# Nova função que envia as justificativas
novo = '''            await fetch("/salvar_integridade_matriz/" + periodo, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ justificativas: window.justificativasSalvas || {} })
            });'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] salvarMatriz alterada para enviar justificativas.")
else:
    print("[ERRO] Linha da funcao salvarMatriz nao encontrada. Tentando variacao...")
    # Tenta com aspas simples ou sem await
    antigo2 = "await fetch('/salvar_integridade_matriz/' + periodo, { method: 'POST' });"
    if antigo2 in c:
        c = c.replace(antigo2, novo.replace('"/salvar_integridade_matriz/"', "'/salvar_integridade_matriz/'"), 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Variacao encontrada e alterada.")
    else:
        print("[ERRO] Nao encontrei a chamada do fetch em salvarMatriz.")
