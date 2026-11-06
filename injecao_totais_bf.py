import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_financeira_bf.html"
shutil.copy2(arq, f"{arq}.bak_injecao_segura_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Adiciona a funcao 'adicionarTotaisBF' no final do script, antes do </script>
funcao_totais = '''
        // === FUNCAO INJETADA: TOTAIS DE INGRESSOS E DISPENDIOS ===
        function adicionarTotaisBF(at) {
            const tb = document.querySelector('#tab tbody');
            if (!tb) return;

            // Evita duplicar se ja existir
            if (document.getElementById('bloco-totais-bf')) return;

            const fmtV = v => (v || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            const safe = (v) => (v && typeof v === 'object') ? v : {atual: 0, anterior: 0};
            
            const rec = safe(at.receitas);
            const desp = safe(at.despesas);
            const extra = safe(at.extra);
            const caixa = safe(at.caixa);

            // Calcula Ingressos
            const totRecAt = rec.total ? rec.total.atual : 0;
            const totRecAnt = rec.total ? rec.total.anterior : 0;
            const totExtAt = extra.recebimentos ? extra.recebimentos.atual : 0;
            const totExtAnt = extra.recebimentos ? extra.recebimentos.anterior : 0;
            const saldoAntAt = caixa.ant ? caixa.ant.atual : (caixa.saldo_anterior ? caixa.saldo_anterior.atual : 0);
            const saldoAntAnt = caixa.ant ? caixa.ant.anterior : (caixa.saldo_anterior ? caixa.saldo_anterior.anterior : 0);

            const totalIngAt = totRecAt + totExtAt + saldoAntAt;
            const totalIngAnt = totRecAnt + totExtAnt + saldoAntAnt;

            // Calcula Dispêndios
            const totDespAt = desp.total ? desp.total.atual : 0;
            const totDespAnt = desp.total ? desp.total.anterior : 0;
            const pagExtAt = extra.pagamentos ? extra.pagamentos.atual : 0;
            const pagExtAnt = extra.pagamentos ? extra.pagamentos.anterior : 0;
            const saldoSegAt = caixa.seg ? caixa.seg.atual : (caixa.saldo_seguinte ? caixa.saldo_seguinte.atual : 0);
            const saldoSegAnt = caixa.seg ? caixa.seg.anterior : (caixa.saldo_seguinte ? caixa.saldo_seguinte.anterior : 0);

            const totalDispAt = totDespAt + pagExtAt + saldoSegAt;
            const totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt;

            // Monta o HTML
            let html = '';
            
            // Bloco Ingressos (Azul)
            html += '<tr id="bloco-totais-bf"><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#0056b3; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE INGRESSOS</td></tr>';
            html += '<tr><td>Receitas Orçamentárias (Corrente + Capital)</td><td style="text-align:right;">' + fmtV(totRecAt) + '</td><td style="text-align:right;">' + fmtV(totRecAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Recebimentos Extraorçamentários</td><td style="text-align:right;">' + fmtV(totExtAt) + '</td><td style="text-align:right;">' + fmtV(totExtAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Saldo em Espécie do Exercício Anterior</td><td style="text-align:right;">' + fmtV(saldoAntAt) + '</td><td style="text-align:right;">' + fmtV(saldoAntAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef; color:#0056b3;"><td>TOTAL DE INGRESSOS</td><td style="text-align:right;">' + fmtV(totalIngAt) + '</td><td style="text-align:right;">' + fmtV(totalIngAnt) + '</td><td style="text-align:right;">-</td></tr>';

            // Bloco Dispêndios (Vermelho)
            html += '<tr><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#dc3545; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE DISPÊNDIOS</td></tr>';
            html += '<tr><td>Despesas Orçamentárias (Corrente + Capital)</td><td style="text-align:right;">' + fmtV(totDespAt) + '</td><td style="text-align:right;">' + fmtV(totDespAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Pagamentos Extraorçamentários</td><td style="text-align:right;">' + fmtV(pagExtAt) + '</td><td style="text-align:right;">' + fmtV(pagExtAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Saldo em Espécie para o Exercício Seguinte</td><td style="text-align:right;">' + fmtV(saldoSegAt) + '</td><td style="text-align:right;">' + fmtV(saldoSegAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef; color:#dc3545;"><td>TOTAL DE DISPÊNDIOS</td><td style="text-align:right;">' + fmtV(totalDispAt) + '</td><td style="text-align:right;">' + fmtV(totalDispAnt) + '</td><td style="text-align:right;">-</td></tr>';

            tb.insertAdjacentHTML('beforeend', html);
        }
'''

# Adiciona a funcao antes do fechamento do script principal
if "function adicionarTotaisBF(at)" not in c:
    idx = c.rfind("</script>")
    if idx != -1:
        c = c[:idx] + funcao_totais + "\n        " + c[idx:]
        print("[OK] Funcao adicionarTotaisBF injetada no HTML.")
    else:
        print("[ERRO] Nao encontrei </script>.")
else:
    print("[AVISO] Funcao adicionarTotaisBF ja existe.")

# 2. Chama a funcao logo apos o render(at, ant) no fetch do carregar()
# Precisamos achar o local exato. Como 'at' e o dado retornado, chamamos antes do '}' do then
# No carregar() original, temos algo como:
# render(a, b);
# Vamos substituir render(a, b); por render(a, b); adicionarTotaisBF(a); se a variavel for 'a'
# Mas o nome pode ser 'dados' ou 'resp'.
# Vamos procurar por "render(" dentro da funcao carregar e injetar depois.

import re
# Procura todas as chamadas de render(qualquer_coisa, qualquer_coisa)
# E adiciona a chamada de adicionarTotaisBF logo depois
matches = re.finditer(r'render\(([^,]+),\s*([^)]+)\);', c)
for match in matches:
    var_at = match.group(1).strip()
    # Injeta adicionarTotaisBF(var_at) logo apos a chamada
    c = c.replace(match.group(), match.group() + f"\n            adicionarTotaisBF({var_at});", 1)

open(arq, "w", encoding="utf-8").write(c)
print("[OK] Chamada de adicionarTotaisBF inserida apos as chamadas de render.")
print("[OK] Arquivo salvo.")
