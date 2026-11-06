import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/analise_financeira_bf.html"
shutil.copy2(arq, f"{arq}.bak_totais_seguro_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# O trecho que desenha o Saldo Seguinte (o último item da tabela original)
antigo = """            html += '<tr><td colspan="4" style="height:10px; border:none;"></td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef;"><td>SALDO EM ESPÉCIE PARA O EXERCÍCIO SEGUINTE</td><td style="text-align:right;">' + fmtV(at.caixa.seg.atual) + '</td><td style="text-align:right;">' + fmtV(at.caixa.seg.anterior) + '</td><td style="text-align:right;">' + fmtP(pct(at.caixa.seg.atual, at.caixa.seg.anterior)) + '</td></tr>';"""

novo = """            html += '<tr><td colspan="4" style="height:10px; border:none;"></td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef;"><td>SALDO EM ESPÉCIE PARA O EXERCÍCIO SEGUINTE</td><td style="text-align:right;">' + fmtV(at.caixa.seg.atual) + '</td><td style="text-align:right;">' + fmtV(at.caixa.seg.anterior) + '</td><td style="text-align:right;">' + fmtP(pct(at.caixa.seg.atual, at.caixa.seg.anterior)) + '</td></tr>';

            // ==========================================
            // INJEÇÃO DOS TOTAIS (via JS puro)
            // ==========================================
            const totRecAt = at.receitas.total.atual || 0;
            const totRecAnt = at.receitas.total.anterior || 0;
            const totExtAt = at.extra.recebimentos.atual || 0;
            const totExtAnt = at.extra.recebimentos.anterior || 0;
            const saldoAntAt = at.caixa.ant.atual || 0;
            const saldoAntAnt = at.caixa.ant.anterior || 0;
            
            const totalIngAt = totRecAt + totExtAt + saldoAntAt;
            const totalIngAnt = totRecAnt + totExtAnt + saldoAntAnt;

            html += '<tr><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#0056b3; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE INGRESSOS (Receita + Extra + Saldo Ant.)</td></tr>';
            html += '<tr><td>Receitas Orçamentárias (Corrente + Capital)</td><td style="text-align:right;">' + fmtV(totRecAt) + '</td><td style="text-align:right;">' + fmtV(totRecAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Recebimentos Extraorçamentários</td><td style="text-align:right;">' + fmtV(totExtAt) + '</td><td style="text-align:right;">' + fmtV(totExtAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Saldo em Espécie do Exercício Anterior</td><td style="text-align:right;">' + fmtV(saldoAntAt) + '</td><td style="text-align:right;">' + fmtV(saldoAntAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef; color:#0056b3;"><td>TOTAL DE INGRESSOS</td><td style="text-align:right;">' + fmtV(totalIngAt) + '</td><td style="text-align:right;">' + fmtV(totalIngAnt) + '</td><td style="text-align:right;">-</td></tr>';

            const totDespAt = at.despesas.total.atual || 0;
            const totDespAnt = at.despesas.total.anterior || 0;
            const pagExtAt = at.extra.pagamentos.atual || 0;
            const pagExtAnt = at.extra.pagamentos.anterior || 0;
            const saldoSegAt = at.caixa.seg.atual || 0;
            const saldoSegAnt = at.caixa.seg.anterior || 0;

            const totalDispAt = totDespAt + pagExtAt + saldoSegAt;
            const totalDispAnt = totDespAnt + pagExtAnt + saldoSegAnt;

            html += '<tr><td colspan="4" style="height:15px; border:none;"></td></tr>';
            html += '<tr style="background:#dc3545; color:#fff; font-weight:bold; font-size:13px;"><td colspan="4">TOTAL GERAL DE DISPÊNDIOS (Despesa + Extra + Saldo Seg.)</td></tr>';
            html += '<tr><td>Despesas Orçamentárias (Corrente + Capital)</td><td style="text-align:right;">' + fmtV(totDespAt) + '</td><td style="text-align:right;">' + fmtV(totDespAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Pagamentos Extraorçamentários</td><td style="text-align:right;">' + fmtV(pagExtAt) + '</td><td style="text-align:right;">' + fmtV(pagExtAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr><td>Saldo em Espécie para o Exercício Seguinte</td><td style="text-align:right;">' + fmtV(saldoSegAt) + '</td><td style="text-align:right;">' + fmtV(saldoSegAnt) + '</td><td style="text-align:right;">-</td></tr>';
            html += '<tr style="font-weight:bold; background:#e9ecef; color:#dc3545;"><td>TOTAL DE DISPÊNDIOS</td><td style="text-align:right;">' + fmtV(totalDispAt) + '</td><td style="text-align:right;">' + fmtV(totalDispAnt) + '</td><td style="text-align:right;">-</td></tr>';"""

if antigo in c:
    c = c.replace(antigo, novo, 1)
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Totais injetados de forma segura no final da tabela.")
else:
    print("[AVISO] Trecho exato nao encontrado. Tentando buscar apenas o final do 'seg'...")
    # Tenta achar a linha do saldo seguinte de forma mais flexivel
    import re
    padrao = re.compile(r"html \+= '<tr style=\"font-weight:bold; background:#e9ecef;\"><td>SALDO EM ESPÉCIE PARA O EXERCÍCIO SEGUINTE</td>.*?</tr>';", re.DOTALL)
    match = padrao.search(c)
    if match:
        # Pega o trecho novo (que comeca no comentario) e concatena
        bloco_extra = novo.split("// ==========================================")[1]
        c = c.replace(match.group(), match.group() + "\n" + bloco_extra, 1)
        open(arq, "w", encoding="utf-8").write(c)
        print("[OK] Totais injetados via regex (fallback).")
    else:
        print("[ERRO] Nao foi possivel encontrar o ponto de insercao.")
