import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_envia_matriz_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Atualiza o fetch de salvarMatriz para enviar a matriz atual
antigo = '''await fetch("/salvar_integridade_matriz/" + periodo, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ justificativas: window.justificativasSalvas || {} })
            });'''

novo = '''await fetch("/salvar_integridade_matriz/" + periodo, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    justificativas: window.justificativasSalvas || {},
                    matriz: window.ultimaMatriz || []
                })
            });'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Fetch atualizado para enviar a matriz.")
else:
    print("[AVISO] Bloco do fetch nao encontrado. Tentando variacao...")
    # Tenta achar o fetch com aspas simples
    antigo2 = "await fetch('/salvar_integridade_matriz/' + periodo, { method: 'POST' });"
    if antigo2 in c:
        c = c.replace(antigo2, novo, 1)
        print("[OK] Variacao encontrada e atualizada.")
    else:
        print("[ERRO] Nao encontrei o fetch de salvarMatriz.")

# Guarda a matriz na variavel global quando renderiza
if "window.ultimaMatriz = matriz;" not in c:
    c = c.replace("function renderizarTabela(matriz) {", "function renderizarTabela(matriz) {\n    window.ultimaMatriz = matriz;", 1)
    print("[OK] Variavel window.ultimaMatriz adicionada na renderizacao.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
