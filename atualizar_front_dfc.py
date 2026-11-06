import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_dfc.html"
shutil.copy2(arq, f"{arq}.bak_layout_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Muda o Título
c = c.replace("Balanço Financeiro Comparativo", "Demonstração do Fluxo de Caixa (DFC)")
c = c.replace("Análise Financeira-BF", "Análise DFC")

# 2. Encontra a funcao 'render' e substitui por uma nova
idx = c.find("function render(at, ant) {")
if idx != -1:
    # Acha o fim da funcao render
    fim = c.find("function carregar()", idx)
    if fim != -1:
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
                return '<tr style="' + trStyle + '">' +
                    '<td>' + label + '</td>' +
                    '<td style="text-align:right;">' + fmtV(va) + '</td>' +
                    '<td style="text-align:right;">' + fmtV(vb) + '</td>' +
                    '<td class="' + cls + '" style="text-align:right;">' + sg + fmtP(v) + '</td>' +
                '</tr>';
            };
            
            const header = (label, color) => '<tr style="background:' + color + '; font-weight:bold; color:#fff;"><td colspan="4">' + label + '</td></tr>';
            
            const at_dados = at.dados || at;
            const ant_dados = ant.dados || ant;

            const op = safe(at_dados.operacional);
            const inv = safe(at_dados.investimento);
            const fin = safe(at_dados.financiamento);
            const cxa = safe(at_dados.caixa);

            let html = '';

            // --- OPERACIONAL ---
            html += header('FLUXO DE CAIXA DAS ATIVIDADES DAS OPERAÇÕES', '#0056b3');
            html += line('Ingressos Operacionais', op.ingressos.atual, op.ingressos.anterior, false);
            html += line('Desembolsos Operacionais', op.desembolsos.atual, op.desembolsos.anterior, false);
            html += line('Caixa Líquido das Operações', op.liquido.atual, op.liquido.anterior, true);
            html += blank();

            // --- INVESTIMENTO ---
            html += header('FLUXO DE CAIXA DAS ATIVIDADES DE INVESTIMENTO', '#e68a8a');
            html += line('Ingressos de Investimento', inv.ingressos.atual, inv.ingressos.anterior, false);
            html += line('Desembolsos de Investimento', inv.desembolsos.atual, inv.desembolsos.anterior, false);
            html += line('Caixa Líquido de Investimento', inv.liquido.atual, inv.liquido.anterior, true);
            html += blank();

            // --- FINANCIAMENTO ---
            html += header('FLUXO DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO', '#dc3545');
            html += line('Ingressos de Financiamento', fin.ingressos.atual, fin.ingressos.anterior, false);
            html += line('Desembolsos de Financiamento', fin.desembolsos.atual, fin.desembolsos.anterior, false);
            html += line('Caixa Líquido de Financiamento', fin.liquido.atual, fin.liquido.anterior, true);
            html += blank();

            // --- APURACAO ---
            html += header('APURAÇÃO DO FLUXO DE CAIXA DO PERÍODO', '#28a745');
            html += line('Geração Líquida de Caixa', cxa.geracao.atual, cxa.geracao.anterior, true);
            html += line('Caixa e Equivalentes Inicial', cxa.inicial.atual, cxa.inicial.anterior, false);
            html += line('Caixa e Equivalentes Final', cxa.final.atual, cxa.final.anterior, true);

            tb.innerHTML = html;
        }
        
        function blank() {
            return '<tr><td colspan="4" style="height:5px; border:none;"></td></tr>';
        }
        
        '''
        c = c[:idx] + nova_render + c[fim:]

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Frontend analise_dfc.html atualizado com a nova estrutura da DFC.")
