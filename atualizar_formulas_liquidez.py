import shutil, datetime, sys

ARQUIVO = r"pc_frontend\liquidez.html"
BACKUP  = f"pc_frontend\\liquidez_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(ARQUIVO, BACKUP)
print(f"[OK] Backup: {BACKUP}\n")

with open(ARQUIVO, "r", encoding="utf-8") as f:
    html = f.read()

# ---------- 1) Aumenta um pouco a largura minima dos cards ----------
html = html.replace(
    "grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));",
    "grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));"
)

# Deixa a formula com quebra de linha mais elegante
html = html.replace(
    ".card .formula { font-size: 11px; color: #888; margin-top: 5px; }",
    ".card .formula { font-size: 11px; color: #666; margin-top: 6px; line-height: 1.4; }"
)

# ---------- 2) Substitui a funcao renderizarResultado ----------
old_fn = '''        function renderizarResultado(data) {
            const res = data.liquidez || {};
            const est = data.estrutura || {};
            const val = data.valores || {};

            let html = '<div class="cards-grid">';

            html += card('Liquidez Imediata', res.liquidez_imediata, 'Caixa / Passivo Circulante');
            html += card('Liquidez Corrente', res.liquidez_corrente, 'Ativo Circulante / Passivo Circulante');
            html += card('Liquidez Seca', res.liquidez_seca, '(Ativo Circulante - Estoques) / Passivo Circulante');
            html += card('Liquidez Geral', res.liquidez_geral, '(Ativo Circulante + Realizável) / (Passivo Circulante + Não Circulante)');

            html += card('Endividamento Geral', (est.endividamento_geral || 0) + '%', 'Passivo Total / Ativo Total');
            html += card('Part. de Capital de Terceiros', (est.part_capital_terceiros || 0) + '%', 'Passivo / PL');
            html += card('Imobilização do PL', (est.imobilizacao_pl || 0) + '%', 'Ativo Permanente / PL');

            html += '</div>';

            document.getElementById('resultado').innerHTML = html;
        }'''

new_fn = '''        function renderizarResultado(data) {
            const res = data.liquidez || {};
            const est = data.estrutura || {};
            const val = data.valores || {};

            function m(v) { return formatarMoeda(v); }

            let html = '<div class="cards-grid">';

            // ---- Liquidez ----
            html += card('Liquidez Imediata', res.liquidez_imediata,
                `Caixa (${m(val.caixa)}) / Passivo Circulante (${m(val.passivo_circulante)})`);

            html += card('Liquidez Corrente', res.liquidez_corrente,
                `Ativo Circulante (${m(val.ativo_circulante)}) / Passivo Circulante (${m(val.passivo_circulante)})`);

            html += card('Liquidez Seca', res.liquidez_seca,
                `(Ativo Circulante (${m(val.ativo_circulante)}) - Estoques (${m(val.estoques)})) / Passivo Circulante (${m(val.passivo_circulante)})`);

            html += card('Liquidez Geral', res.liquidez_geral,
                `(Ativo Circulante (${m(val.ativo_circulante)}) + Realizável (${m(val.realizavel_lp)})) / (Passivo Circulante (${m(val.passivo_circulante)}) + Não Circulante (${m(val.passivo_nao_circulante)}))`);

            // ---- Estrutura ----
            html += card('Endividamento Geral', (est.endividamento_geral || '0,00') + '%',
                `Passivo Total (${m(val.passivo_total)}) / Ativo Total (${m(val.ativo_total)})`);

            html += card('Part. de Capital de Terceiros', (est.part_capital_terceiros || '0,00') + '%',
                `Passivo Total (${m(val.passivo_total)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})`);

            html += card('Imobilização do PL', (est.imobilizacao_pl || '0,00') + '%',
                `Ativo Permanente (${m(val.imobilizado)}) / Patrimônio Líquido (${m(val.patrimonio_liquido)})`);

            html += '</div>';

            document.getElementById('resultado').innerHTML = html;
        }'''

if old_fn not in html:
    print("[ERRO] Funcao renderizarResultado antiga nao encontrada. Abortando.")
    sys.exit(1)

html = html.replace(old_fn, new_fn, 1)

# ---------- 3) Salvar ----------
with open(ARQUIVO, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] liquidez.html atualizado ({len(html):,} chars)")
print("[OK] Cards agora exibem os valores reais em cada formula")
print()
print("=== PROXIMO PASSO ===")
print("1. O servidor uvicorn NAO precisa ser reiniciado (apenas HTML mudou).")
print("2. No navegador: http://127.0.0.1:9994/liquidez")
print("3. Ctrl+Shift+R para limpar cache")
print("4. Clique em Verificar Indices")
