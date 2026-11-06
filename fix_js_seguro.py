import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_fix_js_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Atualizar o fetch para enviar as justificativas
antigo = 'await fetch("/salvar_integridade_matriz/" + periodo, { method: "POST" });'
if antigo not in c:
    antigo = "await fetch('/salvar_integridade_matriz/' + periodo, { method: 'POST' });"

novo = '''await fetch("/salvar_integridade_matriz/" + periodo, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ justificativas: window.justificativasSalvas || {} })
            });'''

if antigo in c:
    c = c.replace(antigo, novo, 1)
    print("[OK] Fetch atualizado.")
else:
    print("[AVISO] Linha exata do fetch nao encontrada. Tentando buscar por 'salvar_integridade_matriz'...")
    # Tenta achar qualquer coisa que pareça a chamada
    import re
    padrao = re.compile(r'await fetch\(.*?/salvar_integridade_matriz/.*?\{\s*method:\s*[\'"]POST[\'"]\s*\}\);')
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        print("[OK] Fetch atualizado via regex.")
    else:
        print("[ERRO] Nao encontrei o fetch de salvar.")

# 2. Adicionar carregarHistorico() após o alert
if 'alert("Matriz salva com sucesso!");' in c:
    c = c.replace('alert("Matriz salva com sucesso!");', 'alert("Matriz e justificativas salvas com sucesso!");\n            carregarHistorico();', 1)
    print("[OK] carregarHistorico() adicionado.")
else:
    print("[AVISO] Texto do alert nao encontrado.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Arquivo salvo.")
