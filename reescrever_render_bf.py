import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_financeira_bf.html"
shutil.copy2(arq, f"{arq}.bak_render_total_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Localiza o inicio da funcao render
idx_inicio = c.find("function render(at, ant) {")
if idx_inicio == -1:
    print("[ERRO] Funcao render nao encontrada.")
    exit(1)

# Localiza o fim da funcao render (proxima funcao ou fechamento)
# Geralmente termina antes de 'function carregar()' ou 'function mp()'
idx_fim = c.find("function carregar()", idx_inicio)
if idx_fim == -1:
    # Tenta achar o proximo 'function'
    idx_fim = c.find("function ", idx_inicio + 20)

if idx_fim == -1:
    print("[ERRO] Fim da funcao render nao encontrado.")
    exit(1)

nova_render = '''function render(at, ant) {
            const tb = document.querySelector('#tab tbody');
            const fmtV = v => (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const fmtP = v => (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%';
            const pct = (a, b) => b !== 0 ? ((a - b) / Math.abs(b)) * 100 : 0;
            const safe = (v) => (v && typeof v === 'object') ? v : {atual: 0, anterior: 0};
            
            const line = (label, va, vb, bold) => {
                const v = pct(va, vb);
                const cls = v >= 0 ? 'pos' : 'neg';
                const sg = v >= 0 ? '+' : '';
                const trStyle = bold ? 'font-weight:bold;' : '';
                const corVa = va < 0 ? 'neg' : '';
                const corVb = vb < 0 ? 'neg' : '';
                return '<tr style="' + trStyle + '">' +
                    '<td>' + label + '</td>' +
                    '<td style="text-align:right;" class="' + corVa + '">' + fmtV(va) + '</td>' +
                    '<td style="text-align:right;" class="' + corVb + '">' + fmtV(vb) + '</td>' +
                    '<td class="' + cls + '" style="text-align:right;">' + sg + fmtP(v) + '</td>' +
                '</tr>';
            };
            
            const header = (label, color) => '<tr style="background:' + color + '; font-weight:bold; color:#fff;"><td colspan="4">' + label + '</td></tr>';
            const blank = () => '<tr><td colspan="4" style="height:10px; border:none;"></td></tr>';
            
            const R = {
                rec: safe(at.receitas),
                desp: safe(at.despesas),
                extra: safe(at.extra),
                caixa: safe(at.caixa)
            };

            let html = '';

            // --- RECEITAS ---
            html += header('RECEITAS', '#0056b3');
            html += line('Receitas Correntes', R.rec.corrente.atual, R.rec.corrente.anterior, false);
            html += line('Receitas de Capital', R.rec.capital.atual, R.rec.capital.anterior, false);
            html += line('Total de Receitas', R.rec.total.atual, R.rec.total.anterior, true);
            html += blank();

            // --- DESPESAS ---
            html += header('DESPESAS', '#dc3545');
            html += line('Despesas Correntes', R.desp.corrente.atual, R.desp.corrente.anterior, false);
            html += line('Despesas de Capital', R.desp.capital.atual, R.desp.capital.anterior, false);
            html += line('Total de Despesas', R.desp.total.atual, R.desp.total.anterior, true);
            html += blank();

            // --- EXTRAORCAMENTARIO ---
            html += header('EXTRAORCAMENTARIO', '#6c757d');
            html += line('Recebimentos Extraorçamentários', R.extra.recebimentos.atual, R.extra.recebimentos.anterior, false);
            html += line('Pagamentos Extraorçamentários', R.extra.pagamentos.atual, R.extra.pagamentos.anterior, false);
            html += blank();

            // --- CAIXA ---
            html += header('CAIXA E EQUIVALENTES', '#28a745');
            html += line('Saldo em Espécie do Exercício Anterior', R.caixa.saldo_anterior.atual, R.caixa.saldo_anterior.anterior, false);
            html += line('Geração Líquida de Caixa', R.caixa.geracao_liquida.atual, R.caixa.geracao_liquida.anterior, true);
            html += line('Saldo em Espécie para o Exercício Seguinte', R.caixa.saldo_seguinte.atual, R.caixa.saldo_seguinte.anterior, true);
            html += blank();

            // === TOTAIS DE INGRESSOS E DISPÊNDIOS ===
            const totRecAt = R.rec.total.atual || 0;
            const totRecAnt = R.rec.total.anterior || 0;
            const totExtAt = R.extra.recebimentos.atual || 0;
            const totExtAnt = R.extra.recebimentos.anterior || 0;
            const saldoAntAt = R.caixa.saldo_anterior.atual || 0;
            const saldoAntAnt = R.caixa.saldo_anterior.anterior || 0;
            
            const totalIngAt = totRecAt + totExtAt + saldoAntAt;
            const totalIngAnt = totRecAnt + totExtAnt + saldoAntAnt;

            html += header('TOTAL GERAL DE INGRESSOS (Receita + Extra + Saldo Ant.)', '#0056b3');
            html += line('Receitas Orçamentárias', totRecAt, totRecAnt, false);
            html += line('Recebimentos Extraorçamentários', totExtAt, totExtAnt, false);
            html += line('Saldo em Espécie do Exercício Anterior', saldoAntAt, saldoAntAnt, false);
            html += line('TOTAL DE INGRESSOS', totalIngAt, totalIngAnt, true);
            html += blank();

            const totDespAt = R.desp.total.atual || 0;
            const totDespAnt = R.desp.total.anterior || 0;
            const pagExtAt = R.extra.pagamentos.atual || 0;
            const pagExtAnt = R.extra.pagamentos.anterior || 0;
            const saldoSegAt = R.caixa.saldo_seguinte.atual || 0;
            const saldoSegAnt = R.caixa.saldo_seguinte.anterior || 0;

            const totalDispAt = totDespAt + pagExtAt + saldoSegAt;
            const totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt;

            html += header('TOTAL GERAL DE DISPÊNDIOS (Despesa + Extra + Saldo Seg.)', '#dc3545');
            html += line('Despesas Orçamentárias', totDespAt, totDespAnt, false);
            html += line('Pagamentos Extraorçamentários', pagExtAt, pagExtAnt, false);
            html += line('Saldo em Espécie para o Exercício Seguinte', saldoSegAt, saldoSegAnt, false);
            html += line('TOTAL DE DISPÊNDIOS', totalDispAt, totalDispAnt, true);

            tb.innerHTML = html;
        }
        '''

c = c[:idx_inicio] + nova_render + c[idx_fim:]
open(arq, "w", encoding="utf-8").write(c)
print("[OK] Funcao render reescrita com os blocos de Ingressos e Dispêndios.")
