html_novo = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Custo de Pessoal - Completo</title>
    <style>
        /* Variáveis de Cores (Padrão Institucional / Google Style) */
        :root {
            --primary: #1a3b5c; /* Azul COFEN */
            --secondary: #2c5282; 
            --bg-light: #f8fafc;
            --text-main: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --success-bg: #f0fff4; --success-text: #276749; --success-border: #9ae6b4;
            --danger-bg: #fff5f5; --danger-text: #c53030; --danger-border: #feb2b2;
            --warning-bg: #fffff0; --warning-text: #b7791f; --warning-border: #faf089;
        }

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 40px;
            background-color: #ffffff;
        }

        /* Cabeçalho */
        .header {
            border-bottom: 3px solid var(--primary);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: var(--primary);
            font-size: 24px;
            font-weight: 700;
            margin: 0 0 5px 0;
            letter-spacing: -0.5px;
        }
        .header p {
            color: var(--text-muted);
            font-size: 14px;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* Seções */
        h2 {
            color: var(--primary);
            font-size: 16px;
            font-weight: 600;
            margin-top: 35px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        h2::before {
            content: "";
            display: inline-block;
            width: 4px;
            height: 16px;
            background-color: var(--secondary);
            margin-right: 10px;
            border-radius: 2px;
        }

        /* Caixa de Fundamentação Legal */
        .legal-box {
            background-color: var(--bg-light);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            font-size: 12px;
            color: #4a5568;
        }
        .legal-box p { margin: 5px 0; }
        .legal-box ul { margin: 5px 0 15px 0; padding-left: 20px; }
        .legal-box li { margin-bottom: 4px; }
        .legal-box strong { color: var(--primary); }

        /* Tabelas Modernas */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 13px;
        }
        th {
            background-color: var(--bg-light);
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            padding: 12px 15px;
            text-align: left;
            border-bottom: 2px solid var(--border-color);
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }
        tr:last-child td { border-bottom: none; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        
        /* Linha de Total */
        .total-row td {
            background-color: var(--bg-light);
            font-weight: 700;
            color: var(--primary);
            border-top: 2px solid var(--border-color);
            border-bottom: 2px solid var(--border-color);
        }

        /* KPIs (Conclusão) */
        .kpi-grid {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .kpi-card {
            flex: 1;
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .kpi-title {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--primary);
        }

        /* Box de Status Final */
        .status-box {
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
            margin-top: 10px;
            border: 1px solid transparent;
        }
        .status-box.success { background-color: var(--success-bg); color: var(--success-text); border-color: var(--success-border); }
        .status-box.warning { background-color: var(--warning-bg); color: var(--warning-text); border-color: var(--warning-border); }
        .status-box.danger { background-color: var(--danger-bg); color: var(--danger-text); border-color: var(--danger-border); }
    </style>
</head>
<body>

    <div class="header">
        <h1>Custo de Pessoal x Limite da Resolução Cofen 814/2026</h1>
        <p>Apuração consolidada 12 meses</p>
    </div>

    <h2>Fundamentação Legal (Resolução Cofen nº 814/2026)</h2>
    <div class="legal-box">
        <p><strong>Art. 2º</strong> O Sistema Cofen/Conselhos Regionais de Enfermagem observará, em relação à despesa total com pessoal, os seguintes limites máximos:</p>
        <ul>
            <li><strong>I – 50%</strong> da Receita Corrente Líquida Ajustada do Conselho Federal de Enfermagem (Cofen);</li>
            <li><strong>II – 60%</strong> da Receita Corrente Líquida Ajustada dos Conselhos Regionais de Enfermagem (Coren).</li>
        </ul>
        <p><strong>§ 1º</strong> Os limites previstos neste artigo constituem instrumentos de governança, planejamento, controle e equilíbrio financeiro, não decorrendo de vinculação normativa à legislação fiscal aplicável à União, Estados, Distrito Federal e Municípios.</p>
        <p><strong>§ 2º</strong> A despesa total com pessoal será apurada pelo regime de competência, mediante a soma da despesa realizada no mês de referência com as dos onze meses imediatamente anteriores.</p>
        <p style="margin-top: 15px;"><strong>Art. 6º</strong> Ficam instituídas as seguintes faixas de controle:</p>
        <ul>
            <li><strong>Cofen:</strong> Alerta (45% a 47,5%) | Prudencial (47,5% a 50%) | Crítica (> 50%).</li>
            <li><strong>Coren:</strong> Alerta (54% a 57%) | Prudencial (57% a 60%) | Crítica (> 60%).</li>
        </ul>
        <p style="font-size: 11px; color: #718096; margin-top: 10px; border-top: 1px solid #e2e8f0; padding-top: 10px;">
            <strong>Composição da Despesa:</strong> Vencimentos, vantagens e encargos sociais; Contribuições previdenciárias; Despesas com contratos de terceirização de mão de obra.
        </p>
    </div>

    <h2>Período e Limites</h2>
    <table>
        <thead>
            <tr>
                <th>Descrição</th>
                <th class="text-right">Valor (R$)</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Receitas Correntes Realizadas - Período Atual</td><td class="text-right" id="rcl-atual">0,00</td></tr>
            <tr><td>Receitas Correntes Realizadas - Período Anterior</td><td class="text-right" id="rcl-anterior">0,00</td></tr>
            <tr class="total-row"><td>Total 12 Meses (RCL)</td><td class="text-right" id="rcl-total">0,00</td></tr>
            <tr class="total-row"><td>Limite Resolução Cofen 814/2026</td><td class="text-right" id="limite-total">0,00</td></tr>
        </tbody>
    </table>

    <h2>Custo de Pessoal Consolidado (12 meses)</h2>
    <table>
        <thead>
            <tr>
                <th>Rubrica</th>
                <th class="text-right">Período Atual (R$)</th>
                <th class="text-right">Período Anterior (R$)</th>
                <th class="text-right">Total 12m (R$)</th>
                <th class="text-right">%</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Pessoal e Encargos Sociais</td><td class="text-right" id="pessoal-atual">0,00</td><td class="text-right" id="pessoal-anterior">0,00</td><td class="text-right" id="pessoal-total">0,00</td><td class="text-right" id="pessoal-pct">0,00%</td></tr>
            <tr><td>Outras Desp. Variáveis - RGPS</td><td class="text-right" id="rgps-atual">0,00</td><td class="text-right" id="rgps-anterior">0,00</td><td class="text-right" id="rgps-total">0,00</td><td class="text-right" id="rgps-pct">0,00%</td></tr>
            <tr><td>Terceirização</td><td class="text-right" id="terc-atual">0,00</td><td class="text-right" id="terc-anterior">0,00</td><td class="text-right" id="terc-total">0,00</td><td class="text-right" id="terc-pct">0,00%</td></tr>
            <tr class="total-row"><td>CUSTO TOTAL (Bruto)</td><td class="text-right" id="custo-atual">0,00</td><td class="text-right" id="custo-anterior">0,00</td><td class="text-right" id="custo-total">0,00</td><td class="text-right">100%</td></tr>
        </tbody>
    </table>

    <h2>Conclusão Detalhada</h2>
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Limite Resolução Cofen 814/2026 (<span id="pct-limite-texto">60%</span> da RCL)</div>
            <div class="kpi-value" id="conclusao-limite">R$ 0,00</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Custo Bruto (12 meses)</div>
            <div class="kpi-value" id="conclusao-custo-pct">0,00%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Custo Ajustado (12 meses)</div>
            <div class="kpi-value" id="conclusao-custo-ajustado">0,00%</div>
        </div>
    </div>
    <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 30px;">Teto estabelecido pela Resolução Cofen 814/2026.</p>

    <h2>Comparativo Final</h2>
    <table>
        <thead>
            <tr>
                <th>Indicador</th>
                <th class="text-right">Valor (R$)</th>
                <th class="text-right">% da RCL</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Receita Corrente Líquida (RCL)</td><td class="text-right" id="final-rcl">0,00</td><td class="text-right">100,00%</td></tr>
            <tr><td>(-) Custo de Pessoal (Bruto)</td><td class="text-right" id="final-custo">0,00</td><td class="text-right" id="final-custo-pct">0,00%</td></tr>
            <tr class="total-row"><td>(=) Margem Disponível (Limite Resolução Cofen 814/2026 - Custo)</td><td class="text-right" id="final-margem">0,00</td><td class="text-right" id="final-margem-pct">0,00%</td></tr>
            <tr><td>Limite Resolução Cofen 814/2026</td><td class="text-right" id="final-limite">0,00</td><td class="text-right" id="final-limite-pct">60,00%</td></tr>
        </tbody>
    </table>

    <div id="final-situacao" class="status-box success">Carregando status...</div>

    <script>
        function fmt(v) {
            return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
        function fmtPct(v) {
            return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';
        }

        const params = new URLSearchParams(window.location.search);
        const periodo = params.get('periodo') || '2026-TRIMESTRE-3';
        const entidade = params.get('entidade') || 'COFEN';

        fetch(`/api/custo_pessoal/${periodo}?entidade=${entidade}&_t=${Date.now()}`, { cache: 'no-store' })
            .then(r => r.json())
            .then(d => {
                const rclTotal = d.rcl_total || 0;
                const custoTotal = d.custo_total || 0;
                const limiteTotal = d.limite_atual || d.limite_total || 0;
                const margemTotal = d.margem_disponivel_atual || (limiteTotal - custoTotal);
                
                const pctLimiteNum = (d.limite_pct || 0.6) * 100;
                const pctLimiteFmt = pctLimiteNum.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';

                document.getElementById('rcl-atual').innerText = fmt(d.rcl_atual || 0);
                document.getElementById('rcl-anterior').innerText = fmt(d.rcl_anterior || 0);
                document.getElementById('rcl-total').innerText = fmt(rclTotal);
                document.getElementById('limite-total').innerText = fmt(limiteTotal);

                document.getElementById('pessoal-atual').innerText = fmt(d.pessoal_atual || 0);
                document.getElementById('pessoal-anterior').innerText = fmt(d.pessoal_anterior || 0);
                document.getElementById('pessoal-total').innerText = fmt(d.pessoal_total || 0);
                document.getElementById('pessoal-pct').innerText = fmtPct((d.pessoal_total / rclTotal) * 100);

                document.getElementById('rgps-atual').innerText = fmt(d.outras_atual || 0);
                document.getElementById('rgps-anterior').innerText = fmt(d.outras_anterior || 0);
                document.getElementById('rgps-total').innerText = fmt(d.outras_total || 0);
                document.getElementById('rgps-pct').innerText = fmtPct((d.outras_total / rclTotal) * 100);

                document.getElementById('terc-atual').innerText = fmt(d.terc_atual || 0);
                document.getElementById('terc-anterior').innerText = fmt(d.terc_anterior || 0);
                document.getElementById('terc-total').innerText = fmt(d.terc_total || 0);
                document.getElementById('terc-pct').innerText = fmtPct((d.terc_total / rclTotal) * 100);

                document.getElementById('custo-atual').innerText = fmt(d.custo_atual || 0);
                document.getElementById('custo-anterior').innerText = fmt(d.custo_anterior || 0);
                document.getElementById('custo-total').innerText = fmt(custoTotal);

                document.getElementById('pct-limite-texto').innerText = pctLimiteFmt;
                document.getElementById('conclusao-limite').innerText = 'R$ ' + fmt(limiteTotal);
                document.getElementById('conclusao-custo-pct').innerText = fmtPct((custoTotal/rclTotal)*100);
                document.getElementById('conclusao-custo-ajustado').innerText = fmtPct((custoTotal/rclTotal)*100);

                document.getElementById('final-rcl').innerText = fmt(rclTotal);
                document.getElementById('final-custo').innerText = fmt(custoTotal);
                document.getElementById('final-custo-pct').innerText = fmtPct((custoTotal/rclTotal)*100);
                document.getElementById('final-margem').innerText = fmt(margemTotal);
                document.getElementById('final-margem-pct').innerText = fmtPct((margemTotal/rclTotal)*100);
                document.getElementById('final-limite').innerText = fmt(limiteTotal);
                document.getElementById('final-limite-pct').innerText = pctLimiteFmt;

                const situacao = document.getElementById('final-situacao');
                // Puxa a regra de negócio do Art. 6º direto do backend
                situacao.innerText = d.faixa_controle || 'Abaixo da Faixa de Alerta (Saudável)';
                
                // Limpa classes anteriores e adiciona a nova
                situacao.className = 'status-box ' + (d.faixa_cor || 'success');
            })
            .catch(e => {
                console.error(e);
                document.getElementById('final-situacao').innerText = 'Erro ao carregar dados.';
            });
    </script>
</body>
</html>
"""

with open('../pc_frontend/custo_pessoal_pdf_completo.html', 'w', encoding='utf-8') as f:
    f.write(html_novo)
print("[OK] Layout do PDF Completo atualizado com design Google/Institucional!")
