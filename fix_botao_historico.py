import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_historico_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Acha a funcao que carrega o historico
idx = c.find("function carregarHistorico")
if idx != -1:
    # Acha o fetch do historico
    trecho = c[idx:idx+1500]
    
    # Quando carrega do historico, ele precisa mostrar o botao salvar
    if "btnSalvar.style.display = 'block';" not in trecho:
        # Procura onde ele renderiza a tabela do historico
        if "renderizarTabela(data.matriz);" in trecho:
            c = c.replace(
                "renderizarTabela(data.matriz);",
                "renderizarTabela(data.matriz);\n            const btnSalvar = document.getElementById('btn-confirmar');\n            if (btnSalvar) { btnSalvar.style.display = 'inline-block'; btnSalvar.innerText = 'Atualizar Justificativas'; btnSalvar.setAttribute('data-periodo', data.periodo || '2026-TRIMESTRE-3'); }",
                1
            )
            print("[OK] Botao 'Atualizar Justificativas' adicionado ao carregar historico.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
