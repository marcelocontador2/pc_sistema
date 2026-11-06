import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. BACKEND: Adicionar campo 'detalhes' (Top 10) à API
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_detalhes_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Localiza a função api_comparativo_despesas_v2
inicio = c_back.find('def api_comparativo_despesas_v2(periodo_atual: str):')
if inicio != -1:
    fim = c_back.find('@app.', inicio + 10)
    if fim == -1: fim = len(c_back)
    
    nova_func = '''def api_comparativo_despesas_v2(periodo_atual: str):
    import os, unicodedata
    upload_dir = r"C:\\\\Users\\\\Marcelo Medeiros\\\\pc_sistema\\\\pc_storage\\\\uploads_raw"
    
    partes = periodo_atual.split("-")
    if len(partes) == 3:
        ano = int(partes[0]); tipo = partes[1]; valor = partes[2]
        periodo_anterior = f"{ano - 1}-{tipo}-{valor}"
    else:
        periodo_anterior = None
        
    def parse_valor(s):
        if not s: return 0.0
        s = s.strip().strip(\'"\').replace(".", "").replace(",", ".").replace("R$", "").strip()
        try: return float(s)
        except: return 0.0
        
    def parse_pct(s):
        if not s: return 0.0
        s = s.strip().strip(\'"\').replace("%", "").replace(",", ".").strip()
        try: return float(s)
        except: return 0.0
        
    def normalizar(txt):
        return unicodedata.normalize(\'NFKD\', txt).encode(\'ASCII\', \'ignore\').decode(\'utf-8\').strip().upper()
        
    def ler_csv(periodo):
        if not periodo: return None
        periodo_formatado = periodo.replace("-", "_")
        arquivo = os.path.join(upload_dir, f"COMPARATIVO_DESPESAS_{periodo_formatado}.csv")
        
        if not os.path.exists(arquivo):
            for f in os.listdir(upload_dir):
                if periodo_formatado in f and "COMPARATIVO_DESPESAS" in f:
                    arquivo = os.path.join(upload_dir, f)
                    break
                    
        if not os.path.exists(arquivo):
            return None
            
        try:
            try:
                with open(arquivo, "r", encoding="utf-8-sig") as f: linhas = f.readlines()
            except UnicodeDecodeError:
                with open(arquivo, "r", encoding="latin-1") as f: linhas = f.readlines()
                
            dados = {
                "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
                "percentual_total": 0.0, "grupos": [], "detalhes": []
            }
            
            grupos_alvo = [
                "PESSOAL E ENCARGOS SOCIAIS",
                "JUROS E ENCARGOS DA DIVIDA",
                "OUTRAS DESPESAS CORRENTES",
                "INVESTIMENTOS",
                "INVERSOES FINANCEIRAS",
                "AMORTIZACAO DA DIVIDA"
            ]
            grupos_alvo_norm = [normalizar(g) for g in grupos_alvo]
            
            # Para o Top 10, coletamos todos os subgrupos que têm valor
            detalhes_temp = []
            
            for linha in linhas:
                if ";" not in linha: continue
                partes_linha = linha.strip().split(";")
                if len(partes_linha) < 4: continue
                
                nome_original = partes_linha[0].strip().strip(\'"\')
                nome_norm = normalizar(nome_original)
                
                if not nome_original or len(nome_original) < 3: continue
                
                # Total Global
                if nome_norm == "CREDITO DISPONIVEL":
                    dados["orcado_total"] = parse_valor(partes_linha[1])
                    dados["empenhado_total"] = parse_valor(partes_linha[2])
                    dados["liquidado_total"] = parse_valor(partes_linha[2])
                    dados["percentual_total"] = parse_pct(partes_linha[3])
                    
                # Grupos contábeis
                if nome_norm in grupos_alvo_norm:
                    if not any(g["nome"] == nome_original for g in dados["grupos"]):
                        dados["grupos"].append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": parse_valor(partes_linha[2]),
                            "liquidado": parse_valor(partes_linha[2]),
                            "percentual": parse_pct(partes_linha[3])
                        })
                
                # Detalhes (para Top 10): excluir os grupos principais, o total e as linhas vazias
                valor_emp = parse_valor(partes_linha[2])
                if valor_emp > 0 and nome_norm not in grupos_alvo_norm and nome_norm != "CREDITO DISPONIVEL":
                    if "CREDITO DISPONIVEL" not in nome_norm and "TOTAL" not in nome_norm:
                        detalhes_temp.append({
                            "nome": nome_original,
                            "orcado": parse_valor(partes_linha[1]),
                            "empenhado": valor_emp,
                            "percentual": parse_pct(partes_linha[3])
                        })
            
            # Ordena por empenhado desc e pega top 10
            detalhes_temp.sort(key=lambda x: x["empenhado"], reverse=True)
            dados["detalhes"] = detalhes_temp[:10]
            
            return dados
        except Exception as e:
            print(f"[ERRO] Falha ao ler CSV: {e}")
            return None
            
    atual = ler_csv(periodo_atual)
    anterior = ler_csv(periodo_anterior)
    
    if not atual:
        return {"erro": True, "mensagem": "Dados nao encontrados para o periodo atual."}
        
    return {
        "erro": False,
        "periodo_atual": periodo_atual,
        "periodo_anterior": periodo_anterior,
        "atual": atual,
        "anterior": anterior or {
            "orcado_total": 0.0, "empenhado_total": 0.0, "liquidado_total": 0.0,
            "percentual_total": 0.0, "grupos": [], "detalhes": []
        }
    }
'''
    
    c_back = c_back[:inicio] + nova_func + c_back[fim:]
    open(back_path, 'w', encoding='utf-8').write(c_back)
    print("[OK] Função api_comparativo_despesas_v2 atualizada com campo 'detalhes' (Top 10)")
else:
    print("[ERRO] Função não encontrada")

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")


# ==========================================
# 2. RELATÓRIO: Reescrever do zero
# ==========================================
rel_path = r"pc_frontend\relatorio_comparativo_despesas.html"
if os.path.exists(rel_path):
    shutil.copy2(rel_path, f"{rel_path}.bak_novo_{ts}")
else:
    print("[INFO] relatorio_comparativo_despesas.html não existe. Vou criar.")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, Helvetica, sans-serif; background: #fff; color: #1e293b; font-size: 12px; line-height: 1.5; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .pagina { padding: 15mm 15mm; page-break-after: always; display: block; width: 100%; min-height: 250mm; }
        .pagina:last-child { page-break-after: auto; }
        .capa-conteudo { padding-top: 80mm; text-align: center; }
        .capa-titulo { font-size: 32px; font-weight: bold; color: #0f172a; margin-bottom: 20px; }
        .capa-subtitulo { font-size: 16px; color: #64748b; margin-bottom: 40px; }
        .capa-periodo { font-size: 14px; color: #3b82f6; font-weight: bold; }
        .titulo-secao { font-size: 18px; font-weight: bold; color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; margin-bottom: 20px; }
        .subtitulo-secao { font-size: 13px; color: #64748b; margin-bottom: 15px; }
        .cards-linha { display: table; width: 100%; table-layout: fixed; border-spacing: 10px 0; margin-bottom: 25px; }
        .card-kpi { display: table-cell; width: 25%; background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 12px; border-radius: 4px; vertical-align: top; }
        .card-kpi-titulo { font-size: 10px; font-weight: bold; color: #64748b; text-transform: uppercase; margin-bottom: 6px; }
        .card-kpi-valor { font-size: 16px; font-weight: bold; color: #0f172a; white-space: nowrap; }
        .card-kpi-sub { font-size: 10px; color: #94a3b8; margin-top: 4px; }
        table.tabela-dados { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; }
        table.tabela-dados th { background: #1e293b; color: #fff; padding: 8px; text-align: left; font-weight: bold; }
        table.tabela-dados td { padding: 7px 8px; border-bottom: 1px solid #e2e8f0; color: #334155; }
        table.tabela-dados tr:nth-child(even) td { background: #f8fafc; }
        .right { text-align: right; }
        .pos { color: #10b981; font-weight: bold; }
        .neg { color: #dc2626; font-weight: bold; }
        .grafico-container { width: 100%; height: 220px; position: relative; margin-bottom: 20px; overflow: hidden; page-break-inside: avoid; }
        .grupo-item { display: block; background: #f8fafc; padding: 10px 15px; margin-bottom: 8px; border-left: 4px solid #ccc; border-radius: 4px; page-break-inside: avoid; }
        .grupo-nome { font-size: 11px; font-weight: bold; color: #64748b; text-transform: uppercase; margin-bottom: 3px; }
        .grupo-valor { font-size: 14px; font-weight: bold; }
        .grupo-descricao { font-size: 10px; color: #94a3b8; margin-top: 2px; }
        .caixa-conclusao { background: #0f172a; color: #fff; padding: 15px; border-radius: 6px; margin-top: 15px; }
        .caixa-conclusao-titulo { font-size: 14px; color: #60a5fa; font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 12px; }
        .conclusao-linha { padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 11px; line-height: 1.5; }
        .conclusao-linha:last-child { border-bottom: none; }
        @media print { .pagina { page-break-after: always; } .pagina:last-child { page-break-after: auto; } .grafico-container { page-break-inside: avoid; } .btn, .no-print { display: none !important; } }
    </style>
</head>
<body>

<div class="pagina">
    <div class="capa-conteudo">
        <div class="capa-titulo">Relatório de Despesas</div>
        <div class="capa-subtitulo">Análise Comparativa de Gastos - COFEN/CORENs</div>
        <div class="capa-periodo" id="capa-periodo">Carregando...</div>
    </div>
</div>

<div class="pagina">
    <div class="titulo-secao">Sumário Executivo</div>
    <p class="subtitulo-secao" id="resumo-texto">Carregando...</p>

    <div class="cards-linha">
        <div class="card-kpi">
            <div class="card-kpi-titulo">Total Orçado</div>
            <div class="card-kpi-valor" id="kpi-orcado">R$ 0,00</div>
            <div class="card-kpi-sub" id="kpi-orcado-ant">Ant: R$ 0,00</div>
        </div>
        <div class="card-kpi">
            <div class="card-kpi-titulo">Total Empenhado</div>
            <div class="card-kpi-valor" id="kpi-empenhado">R$ 0,00</div>
            <div class="card-kpi-sub" id="kpi-empenhado-ant">Ant: R$ 0,00</div>
        </div>
        <div class="card-kpi">
            <div class="card-kpi-titulo">Execução Orçamentária</div>
            <div class="card-kpi-valor" id="kpi-execucao">0,00%</div>
            <div class="card-kpi-sub" id="kpi-execucao-var">+0,00 p.p.</div>
        </div>
        <div class="card-kpi">
            <div class="card-kpi-titulo">Variação Empenhada</div>
            <div class="card-kpi-valor" id="kpi-variacao">0,00%</div>
            <div class="card-kpi-sub" id="kpi-variacao-ant">Atual vs Anterior</div>
        </div>
    </div>

    <div class="subtitulo-secao" style="font-weight: bold; font-size: 14px; color: #0f172a; margin-top: 20px;">Indicadores Comparativos</div>
    <table class="tabela-dados">
        <thead>
            <tr>
                <th>Indicador</th>
                <th class="right">Período Atual</th>
                <th class="right">Período Anterior</th>
                <th class="right">Variação</th>
            </tr>
        </thead>
        <tbody id="tabela-indicadores"></tbody>
    </table>
</div>

<div class="pagina">
    <div class="titulo-secao">Grupos Contábeis</div>
    <p class="subtitulo-secao">Comparativo entre período atual e anterior (valores em R$ milhões).</p>
    <div class="grafico-container"><canvas id="grafico-grupos"></canvas></div>
    <div id="lista-grupos"></div>
</div>

<div class="pagina">
    <div class="titulo-secao">Top 10 Maiores Gastos</div>
    <p class="subtitulo-secao">Subgrupos com maior valor empenhado no período atual.</p>
    <table class="tabela-dados">
        <thead>
            <tr>
                <th>#</th>
                <th>Descrição do Gasto</th>
                <th class="right">Orçado (R$)</th>
                <th class="right">Empenhado (R$)</th>
                <th class="right">% Execução</th>
            </tr>
        </thead>
        <tbody id="tabela-top10"></tbody>
    </table>
</div>

<div class="pagina">
    <div class="titulo-secao">Saldo a Realizar e Conclusão</div>
    <div class="cards-linha">
        <div class="card-kpi" style="border-left-color: #f59e0b; display: block; width: 100%;">
            <div class="card-kpi-titulo">Meta Orçamentária Anual</div>
            <div class="card-kpi-valor" id="meta-anual">R$ 0,00</div>
        </div>
        <div class="card-kpi" style="border-left-color: #10b981; display: block; width: 100%;">
            <div class="card-kpi-titulo">Já Empenhado</div>
            <div class="card-kpi-valor" id="ja-empenhado">R$ 0,00</div>
        </div>
        <div class="card-kpi" style="border-left-color: #ef4444; display: block; width: 100%;">
            <div class="card-kpi-titulo">Saldo Restante</div>
            <div class="card-kpi-valor" id="saldo-restante">R$ 0,00</div>
        </div>
    </div>
    <div class="caixa-conclusao">
        <div class="caixa-conclusao-titulo">Conclusão e Análise</div>
        <div id="lista-conclusao"></div>
    </div>
</div>

<script>
    function fmtMi(v) {
        if (v === undefined || v === null) return "R$ 0,00 mi";
        const num = Number(v) / 1000000;
        const sinal = num < 0 ? "-R$ " : "R$ ";
        return sinal + Math.abs(num).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " mi";
    }
    function fmt(v) {
        if (v === undefined || v === null) return "R$ 0,00";
        const sinal = v < 0 ? "-R$ " : "R$ ";
        return sinal + Math.abs(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    function fmtPct(v) {
        if (v === undefined || v === null) return "0,00%";
        return (v >= 0 ? "+" : "") + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }
    function fmtPp(v) {
        if (v === undefined || v === null) return "0,00 p.p.";
        return (v >= 0 ? "+" : "") + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " p.p.";
    }
    function capitalizeNome(nome) {
        return nome.toLowerCase().split(' ').map(function(p) {
            if (p.length > 2) return p.charAt(0).toUpperCase() + p.slice(1);
            return p;
        }).join(' ');
    }

    const urlParams = new URLSearchParams(window.location.search);
    const historicoId = urlParams.get('historico_id');

    async function carregarDados() {
        try {
            let dadosFinal = null;
            let periodoUsar = "2026-TRIMESTRE-3";

            if (historicoId) {
                const resHist = await fetch(`/historico_comparativo_despesas/${historicoId}`);
                const histData = await resHist.json();
                periodoUsar = histData.periodo || "2026-TRIMESTRE-3";
                let histDados = histData.dados;
                if (typeof histDados === 'string') { try { histDados = JSON.parse(histDados); } catch(e) { histDados = null; } }
                if (histDados && histDados.atual && histDados.anterior) {
                    dadosFinal = histDados;
                } else {
                    const resApi = await fetch(`/api/comparativo_despesas_v2/${periodoUsar}`);
                    dadosFinal = await resApi.json();
                }
            } else {
                const resApi = await fetch(`/api/comparativo_despesas_v2/${periodoUsar}`);
                dadosFinal = await resApi.json();
            }

            if (!dadosFinal || dadosFinal.erro) throw new Error("Sem dados");
            if (!dadosFinal.atual || !dadosFinal.anterior) throw new Error("Formato inválido");

            const at = dadosFinal.atual;
            const an = dadosFinal.anterior;
            const periodoExibir = dadosFinal.periodo_atual || periodoUsar;

            document.getElementById('capa-periodo').innerText = 'Período: ' + periodoExibir;

            const varEmpenhado = an.empenhado_total > 0 ? ((at.empenhado_total - an.empenhado_total) / an.empenhado_total) * 100 : 0;
            const varExec = at.percentual_total - an.percentual_total;
            const varOrc = an.orcado_total > 0 ? ((at.orcado_total - an.orcado_total) / an.orcado_total) * 100 : 0;

            document.getElementById('resumo-texto').innerHTML = 
                'O total empenhado no período atingiu <strong>' + fmt(at.empenhado_total) + 
                '</strong>, contra <strong>' + fmt(an.empenhado_total) + 
                '</strong> no período anterior, uma variação de <strong>' + fmtPct(varEmpenhado) + '</strong>.';

            document.getElementById('kpi-orcado').innerText = fmtMi(at.orcado_total);
            document.getElementById('kpi-orcado-ant').innerText = 'Ant: ' + fmtMi(an.orcado_total);
            document.getElementById('kpi-empenhado').innerText = fmtMi(at.empenhado_total);
            document.getElementById('kpi-empenhado-ant').innerText = 'Ant: ' + fmtMi(an.empenhado_total);
            document.getElementById('kpi-execucao').innerText = fmt(at.percentual_total) + '%';
            document.getElementById('kpi-execucao-var').innerText = fmtPp(varExec);
            document.getElementById('kpi-execucao-var').style.color = varExec >= 0 ? '#10b981' : '#dc2626';
            document.getElementById('kpi-variacao').innerText = fmtPct(varEmpenhado);
            document.getElementById('kpi-variacao').style.color = varEmpenhado >= 0 ? '#dc2626' : '#10b981';

            document.getElementById('tabela-indicadores').innerHTML = 
                '<tr><td>Total Orçado</td><td class="right">' + fmt(at.orcado_total) + '</td><td class="right">' + fmt(an.orcado_total) + '</td><td class="right ' + (varOrc >= 0 ? 'pos' : 'neg') + '">' + fmtPct(varOrc) + '</td></tr>' +
                '<tr><td>Total Empenhado</td><td class="right">' + fmt(at.empenhado_total) + '</td><td class="right">' + fmt(an.empenhado_total) + '</td><td class="right ' + (varEmpenhado >= 0 ? 'pos' : 'neg') + '">' + fmtPct(varEmpenhado) + '</td></tr>' +
                '<tr><td>Execução Orçamentária</td><td class="right">' + fmt(at.percentual_total) + '%</td><td class="right">' + fmt(an.percentual_total) + '%</td><td class="right ' + (varExec >= 0 ? 'pos' : 'neg') + '">' + fmtPp(varExec) + '</td></tr>';

            const gruposAt = at.grupos || [];
            const gruposAn = an.grupos || [];
            const labels = gruposAt.map(function(g) { return capitalizeNome(g.nome); });
            const valsAt = gruposAt.map(function(g) { return g.empenhado || 0; });
            const valsAn = gruposAt.map(function(g) {
                const m = gruposAn.find(function(x) { return x.nome === g.nome; });
                return m ? (m.empenhado || 0) : 0;
            });

            new Chart(document.getElementById('grafico-grupos'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Empenhado Atual', data: valsAt, backgroundColor: '#1e293b' },
                        { label: 'Empenhado Anterior', data: valsAn, backgroundColor: '#60a5fa' }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top', labels: { font: { size: 10 } } } },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + (v/1000000).toFixed(0) + ' mi'; }, font: { size: 9 } } },
                        x: { ticks: { font: { size: 9 } } }
                    }
                }
            });

            let htmlGrupos = '';
            gruposAt.forEach(function(g) {
                const valorAtual = g.empenhado || 0;
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).empenhado || 0;
                const variacao = valorAtual - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const cor = variacao >= 0 ? '#dc2626' : '#10b981';
                const seta = variacao >= 0 ? '▲' : '▼';
                
                htmlGrupos += 
                    '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
                        '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
                        '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                            '<div style="font-size: 13px; color: #1e293b;"><strong>Empenhado:</strong> ' + fmt(valorAtual) + '</div>' +
                            '<div style="font-size: 11px; color: #64748b;">Anterior: ' + (anterior > 0 ? fmt(anterior) : '—') + '</div>' +
                        '</div>' +
                        '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' + seta + ' ' + fmt(variacao) + ' (' + (anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores') + ')</div>' +
                    '</div>';
            });
            const divGrupos = document.getElementById('lista-grupos');
            if (divGrupos) divGrupos.innerHTML = htmlGrupos;

            const detalhes = at.detalhes || [];
            let htmlTop10 = '';
            detalhes.forEach(function(d, i) {
                const pct = d.orcado > 0 ? (d.empenhado / d.orcado) * 100 : 0;
                htmlTop10 += 
                    '<tr>' +
                        '<td>' + (i + 1) + '</td>' +
                        '<td>' + capitalizeNome(d.nome) + '</td>' +
                        '<td class="right">' + fmt(d.orcado) + '</td>' +
                        '<td class="right">' + fmt(d.empenhado) + '</td>' +
                        '<td class="right">' + fmt(pct) + '%</td>' +
                    '</tr>';
            });
            const tbodyTop10 = document.getElementById('tabela-top10');
            if (tbodyTop10) tbodyTop10.innerHTML = htmlTop10;

            const meta = at.orcado_total;
            const empenhado = at.empenhado_total;
            const saldo = meta - empenhado;

            document.getElementById('meta-anual').innerText = fmtMi(meta);
            document.getElementById('ja-empenhado').innerText = fmtMi(empenhado);
            document.getElementById('saldo-restante').innerText = fmtMi(saldo);

            let htmlConc = '';
            gruposAt.forEach(function(g) {
                const anterior = (gruposAn.find(function(x) { return x.nome === g.nome; }) || {}).empenhado || 0;
                const variacao = (g.empenhado || 0) - anterior;
                const pct = anterior > 0 ? (variacao / anterior) * 100 : 0;
                const seta = variacao >= 0 ? '▲' : '▼';
                htmlConc += 
                    '<div class="conclusao-linha">' +
                        seta + ' <strong>' + capitalizeNome(g.nome) + ':</strong> ' + 
                        (variacao >= 0 ? 'Aumento' : 'Redução') + ' de ' + fmtMi(Math.abs(variacao)) + ' (' + fmtPct(pct) + ')' +
                    '</div>';
            });
            htmlConc += 
                '<div class="conclusao-linha">' +
                    '<strong>Saldo a Realizar:</strong> Restam ' + fmtMi(saldo) + ' para atingir o orçamento anual.' +
                '</div>';

            document.getElementById('lista-conclusao').innerHTML = htmlConc;

        } catch (e) {
            console.error("Erro:", e);
            const el = document.getElementById('resumo-texto');
            if (el) el.innerText = 'Erro: ' + e.message;
        }
    }

    document.addEventListener('DOMContentLoaded', carregarDados);
</script>
</body>
</html>"""

with open(rel_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Relatório de despesas reescrito do zero com 5 páginas!")

print("\n" + "=" * 70)
print("PRÓXIMOS PASSOS")
print("=" * 70)
print("1. REINICIE o servidor (obrigatório - alteramos main.py)")
print("2. Gere o PDF pela tela de Comparativo de Despesas")
print("3. O PDF deve ter: Capa, Sumário, Grupos Contábeis, Top 10, Conclusão")
