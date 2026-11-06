import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_bp.html"
shutil.copy2(arq, f"{arq}.bak_total_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Substitui o bloco de render para incluir Total do Ativo e Total do Passivo
antigo_render = """let html = '';
            html += linha('Ativo Circulante', d.ativo_circulante.atual, d.ativo_circulante.anterior);
            html += linha('Caixa e Equivalentes', d.caixa.atual, d.caixa.anterior);
            html += linha('Créditos a Curto Prazo', d.creditos.atual, d.creditos.anterior);
            html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);
            html += linha('Passivo Circulante', d.passivo_circulante.atual, d.passivo_circulante.anterior);
            html += linha('Passivo Não Circulante', d.passivo_nao_circulante.atual, d.passivo_nao_circulante.anterior);
            html += linha('Patrimônio Líquido', d.patrimonio_liquido.atual, d.patrimonio_liquido.anterior);
            tb.innerHTML = html;"""

novo_render = """let html = '';
            html += linha('Ativo Circulante', d.ativo_circulante.atual, d.ativo_circulante.anterior);
            html += linha('Caixa e Equivalentes', d.caixa.atual, d.caixa.anterior);
            html += linha('Créditos a Curto Prazo', d.creditos.atual, d.creditos.anterior);
            html += linha('Ativo Não Circulante', d.ativo_nao_circulante.atual, d.ativo_nao_circulante.anterior);
            html += linha('Imobilizado', d.imobilizado.atual, d.imobilizado.anterior);
            html += linha('TOTAL DO ATIVO', d.total_ativo.atual, d.total_ativo.anterior);
            html += linha('Passivo Circulante', d.passivo_circulante.atual, d.passivo_circulante.anterior);
            html += linha('Passivo Não Circulante', d.passivo_nao_circulante.atual, d.passivo_nao_circulante.anterior);
            html += linha('TOTAL DO PASSIVO', d.total_passivo.atual, d.total_passivo.anterior);
            html += linha('Patrimônio Líquido', d.patrimonio_liquido.atual, d.patrimonio_liquido.anterior);
            tb.innerHTML = html;"""

if antigo_render in c:
    c = c.replace(antigo_render, novo_render)
    print("[OK] Linhas 'Total do Ativo' e 'Total do Passivo' adicionadas na tabela.")
else:
    print("[AVISO] Trecho do render nao encontrado. Tentando variacao...")

# 2. Ajusta a funcao linha para mostrar '-' quando anterior = 0
antigo_linha = """const linha = (label, va, vb) => {
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

novo_linha = """const linha = (label, va, vb) => {
                const v = pct(va, vb);
                const cls = parseFloat(v) >= 0 ? 'pos' : 'neg';
                const sg = parseFloat(v) >= 0 ? '+' : '';
                const val_ant = (vb === 0) ? '-' : fmtMil(vb);
                const var_pct = (vb === 0) ? '-' : sg + v;
                return `<tr>
                    <td>${label}</td>
                    <td>${fmtMil(va)}</td>
                    <td>${val_ant}</td>
                    <td class="${cls}">${var_pct}</td>
                </tr>`;
            };"""

if antigo_linha in c:
    c = c.replace(antigo_linha, novo_linha)
    print("[OK] Funcao 'linha' ajustada para mostrar '-' quando anterior = 0.")

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend ajustado.")
