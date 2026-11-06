import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_ordem_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Troca o cabecalho da tabela (2025 -> Periodo Anterior, 2026 -> Periodo Atual)
c = c.replace("<th>2025 (R$ mi)</th>", "<th>Período Atual (R$ mi)</th>")
c = c.replace("<th>2026 (R$ mi)</th>", "<th>Período Anterior (R$ mi)</th>")

# 2. Troca a ordem dos valores na funcao render (va = atual, vb = anterior)
# A funcao original tem fmtMil(vb) e fmtMil(va) - precisamos inverter
antigo_render = """const linha = (label, va, vb) => {
                const v = pct(va, vb);
                const cls = parseFloat(v) >= 0 ? 'pos' : 'neg';
                const sg = parseFloat(v) >= 0 ? '+' : '';
                return `<tr>
                    <td>${label}</td>
                    <td>${fmtMil(vb)}</td>
                    <td>${fmtMil(va)}</td>
                    <td class="${cls}">${sg}${v}</td>
                </tr>`;
            };"""

novo_render = """const linha = (label, va, vb) => {
                const v = pct(va, vb);
                const cls = parseFloat(v) >= 0 ? 'pos' : 'neg';
                const sg = parseFloat(v) >= 0 ? '+' : '';
                return `<tr>
                    <td>${label}</td>
                    <td>${fmtMil(va)}</td>
                    <td>${fmtMil(vb)}</td>
                    <td class="${cls}">${sg}${v}</td>
                </tr>`;
            };"""

if antigo_render in c:
    c = c.replace(antigo_render, novo_render)
    print("[OK] Ordem dos valores ajustada (atual primeiro).")

# 3. Garante que as chamadas de linha estao passando (atual, anterior)
# (A API retorna {atual: ..., anterior: ...})

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend ajustado.")
