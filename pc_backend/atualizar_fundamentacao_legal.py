c = open('../pc_frontend/custo_pessoal_pdf_completo.html', encoding='utf-8-sig').read()

# 1. Substituir a seção de Fundamentação Legal
antiga_fundamentacao = """<h2>Fundamentação Legal</h2>
    <p style="font-size: 13px; text-align: justify;">
        <strong>Resolução Cofen nº 814/2026:</strong> A despesa total com pessoal não poderá exceder o limite de 60% da Receita Corrente Líquida (RCL) para os Conselhos Regionais (COREN) e 50% para o Conselho Federal (COFEN).<br>
        <strong>Composição da Despesa:</strong> Vencimentos, vantagens e encargos sociais; Contribuições previdenciárias; Despesas com contratos de terceirização de mão de obra.
    </p>"""

nova_fundamentacao = """<h2>Fundamentação Legal (Resolução Cofen nº 814/2026)</h2>
    <div style="font-size: 12px; text-align: justify; line-height: 1.5; background: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd;">
        <p><strong>Art. 2º</strong> O Sistema Cofen/Conselhos Regionais de Enfermagem observará, em relação à despesa total com pessoal, os seguintes limites máximos:</p>
        <ul>
            <li><strong>I – 50%</strong> da Receita Corrente Líquida Ajustada do Conselho Federal de Enfermagem (Cofen);</li>
            <li><strong>II – 60%</strong> da Receita Corrente Líquida Ajustada dos Conselhos Regionais de Enfermagem (Coren).</li>
        </ul>
        <p><strong>§ 1º</strong> Os limites previstos neste artigo constituem instrumentos de governança, planejamento, controle e equilíbrio financeiro, não decorrendo de vinculação normativa à legislação fiscal aplicável à União, Estados, Distrito Federal e Municípios.</p>
        <p><strong>§ 2º</strong> A despesa total com pessoal será apurada pelo regime de competência, mediante a soma da despesa realizada no mês de referência com as dos onze meses imediatamente anteriores.</p>
        
        <p style="margin-top: 10px;"><strong>Art. 6º</strong> Ficam instituídas as seguintes faixas de controle:</p>
        <ul>
            <li><strong>Cofen:</strong> Alerta (45% a 47,5%) | Prudencial (47,5% a 50%) | Crítica (> 50%).</li>
            <li><strong>Coren:</strong> Alerta (54% a 57%) | Prudencial (57% a 60%) | Crítica (> 60%).</li>
        </ul>
        <p style="margin-top: 10px; font-size: 11px; color: #555;"><strong>Composição da Despesa:</strong> Vencimentos, vantagens e encargos sociais; Contribuições previdenciárias; Despesas com contratos de terceirização de mão de obra.</p>
    </div>"""

if antiga_fundamentacao in c:
    c = c.replace(antiga_fundamentacao, nova_fundamentacao)
    print("[OK] Fundamentação Legal atualizada com os Artigos 2º e 6º!")

# 2. Atualizar a lógica de "Situação" no JavaScript
antiga_situacao = """
                const situacao = document.getElementById('final-situacao');
                if (custoTotal <= limiteTotal) {
                    situacao.innerText = 'Dentro do limite legal (<= ' + pctLimiteFmt + ')';
                    situacao.className = 'success';
                } else {
                    situacao.innerText = 'Acima do limite legal (> ' + pctLimiteFmt + ')';
                    situacao.className = 'danger';
                }
"""

nova_situacao = """
                const situacao = document.getElementById('final-situacao');
                const pctCusto = (custoTotal / rclTotal) * 100;
                const isCoren = (entidade.toUpperCase() === 'COREN');
                
                let statusTexto = '';
                let statusClasse = '';

                // Lógica baseada nas Faixas de Controle do Art. 6º
                if (isCoren) {
                    if (pctCusto > 60) { statusTexto = 'Faixa Crítica (> 60%)'; statusClasse = 'danger'; }
                    else if (pctCusto >= 57) { statusTexto = 'Faixa Prudencial (57% a 60%)'; statusClasse = 'warning'; }
                    else if (pctCusto >= 54) { statusTexto = 'Faixa de Alerta (54% a 57%)'; statusClasse = 'warning'; }
                    else { statusTexto = 'Abaixo da Faixa de Alerta (Saudável)'; statusClasse = 'success'; }
                } else { // COFEN
                    if (pctCusto > 50) { statusTexto = 'Faixa Crítica (> 50%)'; statusClasse = 'danger'; }
                    else if (pctCusto >= 47.5) { statusTexto = 'Faixa Prudencial (47,5% a 50%)'; statusClasse = 'warning'; }
                    else if (pctCusto >= 45) { statusTexto = 'Faixa de Alerta (45% a 47,5%)'; statusClasse = 'warning'; }
                    else { statusTexto = 'Abaixo da Faixa de Alerta (Saudável)'; statusClasse = 'success'; }
                }

                situacao.innerText = statusTexto;
                situacao.className = statusClasse;
"""

if antiga_situacao in c:
    c = c.replace(antiga_situacao, nova_situacao)
    print("[OK] Lógica de Faixas de Controle (Art. 6º) implementada no JavaScript!")

# Adicionar estilo para a classe warning (se não existir)
if ".warning" not in c:
    c = c.replace(".danger { color: #dc3545; font-weight: bold; }", 
                  ".danger { color: #dc3545; font-weight: bold; }\n        .warning { color: #ffc107; font-weight: bold; }")

open('../pc_frontend/custo_pessoal_pdf_completo.html', 'w', encoding='utf-8').write(c)
