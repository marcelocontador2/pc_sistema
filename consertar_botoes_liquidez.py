import shutil, os, re

arquivo = r"pc_frontend\liquidez.html"
backup = r"pc_frontend\liquidez_backup_ajuste_20261105_165509.html"

# 1. Restaura o arquivo do backup (antes da quebra)
if os.path.exists(backup):
    shutil.copy2(backup, arquivo)
    print("[OK] Arquivo restaurado a partir do backup.")
else:
    print("[ERRO] Backup não encontrado. Avise-me.")

# 2. Aplica a correção cirúrgica no JS
with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(r"function renderizarResultado\(data\) \{.*?document\.getElementById\('resultado'\)\.innerHTML = html;\s*\}", re.DOTALL)

new_func = """function renderizarResultado(data) {
            const res = data.liquidez || {};
            const est = data.estrutura || {};
            const val = data.valores || {};

            function m(v) { return formatarMoeda(v); }

            let html = '<div class="cards-grid">';

            // ---- Liquidez (com aviso de "vezes") ----
            html += card('Liquidez Imediata', res.liquidez_imediata,
                `Caixa (${m(val.caixa)}) / Passivo Circulante (${m(val.passivo_circulante)}) <br><span style="color:#0056b3; font-weight:bold; font-size:11px;">Resultado em vezes (R$ por R$ 1,00 de dívida)</span>`);

            html += card('Liquidez Corrente', res.liquidez_corrente,
                `Ativo Circulante (${m(val.ativo_circulante)}) / Passivo Circulante (${m(val.passivo_circulante)}) <br><span style="color:#0056b3; font-weight:bold; font-size:11px;">Resultado em vezes (R$ por R$ 1,00 de dívida)</span>`);

            html += card('Liquidez Seca', res.liquidez_seca,
                `(Ativo Circulante (${m(val.ativo_circulante)}) - Estoques (${m(val.estoques)})) / Passivo Circulante (${m(val.passivo_circulante)}) <br><span style="color:#0056b3; font-weight:bold; font-size:11px;">Resultado em vezes (R$ por R$ 1,00 de dívida)</span>`);

            html += card('Liquidez Geral', res.liquidez_geral,
                `(Ativo Circulante (${m(val.ativo_circulante)}) + Realizável (${m(val.realizavel_lp)})) / (Passivo Circulante (${m(val.passivo_circulante)}) + Não Circulante (${m(val.passivo_nao_circulante)})) <br><span style="color:#0056b3; font-weight:bold; font-size:11px;">Resultado em vezes (R$ por R$ 1,00 de dívida)</span>`);

            // ---- Estrutura (com x100 explícito) ----
            html += card('Endividamento Geral', (est.endividamento_geral || '0,00') + '%',
                `(Passivo Total (${m(val.passivo_total)}) / Ativo Total (${m(val.ativo_total)})) × 100`);

            html += card('Part. de Capital de Terceiros', (est.part_capital_terceiros || '0,00') + '%',
                `(Passivo Total (${m(val.passivo_total)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})) × 100`);

            html += card('Imobilização do PL', (est.imobilizacao_pl || '0,00') + '%',
                `(Ativo Permanente (${m(val.imobilizado)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})) × 100`);

            html += '</div>';

            document.getElementById('resultado').innerHTML = html;
        }"""

if pattern.search(html):
    html = pattern.sub(new_func, html)
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] JavaScript blindado e corrigido. Botoes devem voltar a funcionar.")
else:
    print("[ERRO] Nao foi possivel encontrar a funcao no arquivo restaurado.")
