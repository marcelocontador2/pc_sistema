import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_vermelho_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Substitui a funcao 'line' dentro de 'render' para colorir valores negativos
antigo = """            const line = (label, va, vb, bold, classe) => {
                const v = pct(va, vb);
                const cls = v >= 0 ? 'pos' : 'neg';
                const sg = v >= 0 ? '+' : '';
                const trStyle = bold ? 'bold-row' : '';
                return `<tr class="${trStyle}">
                    <td>${label}</td>
                    <td class="right">${fmt(va)}</td>
                    <td class="right">${fmt(vb)}</td>
                    <td class="right ${cls}">${sg}${fmt(v)}</td>
                </tr>`;
            };"""

novo = """            const line = (label, va, vb, bold, classe) => {
                const v = pct(va, vb);
                const cls = v >= 0 ? 'pos' : 'neg';
                const sg = v >= 0 ? '+' : '';
                const trStyle = bold ? 'bold-row' : '';
                
                // Define a cor do valor (vermelho se negativo, senao normal)
                const corVa = va < 0 ? 'neg' : '';
                const corVb = vb < 0 ? 'neg' : '';
                
                return `<tr class="${trStyle}">
                    <td>${label}</td>
                    <td class="right ${corVa}">${fmt(va)}</td>
                    <td class="right ${corVb}">${fmt(vb)}</td>
                    <td class="right ${cls}">${sg}${fmt(v)}</td>
                </tr>`;
            };"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao line ajustada: valores negativos ficarao em vermelho.")
else:
    print("[AVISO] Nao encontrei o bloco exato. Tentando variacao...")
    # Tenta achar a funcao line por regex (mais flexivel)
    import re
    padrao = re.compile(r'const line = \(label, va, vb, bold, classe\) => \{.*?\};', re.DOTALL)
    match = padrao.search(c)
    if match:
        c = c.replace(match.group(), novo, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Funcao line ajustada via regex.")
    else:
        print("[ERRO] Nao foi possivel encontrar a funcao line para substituir.")
