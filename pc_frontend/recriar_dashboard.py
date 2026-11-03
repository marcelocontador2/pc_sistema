html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard de Despesas - SGPC</title>
    <style>
        :root {
            --primary: #2b6cb0;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --text: #2d3748;
            --text-light: #718096;
            --green: #38a169;
            --red: #e53e3e;
        }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--text); }
        .container { max-width: 1200px; margin: 0 auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: var(--card-bg); padding: 15px 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .header h1 { margin: 0; font-size: 22px; color: var(--primary); }
        .filters { display: flex; gap: 10px; align-items: center; }
        .filters select { padding: 6px; border: 1px solid #cbd5e0; border-radius: 4px; font-size: 14px; }
        .btn { background: var(--primary); color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #2c5282; }

        /* Título do Bloco - Sem a linha azul na esquerda, centralizado com linha embaixo */
        .section-title { 
            font-size: 18px; 
            font-weight: 700; 
            margin: 30px 0 15px 0; 
            color: var(--text); 
            text-align: center; 
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            text-transform: uppercase;
        }
        
        .cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .card { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid var(--primary); }
        .card-title { font-size: 13px; text-transform: uppercase; color: var(--text-light); font-weight: bold; margin-bottom: 10px; }
        .card-value { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .card-sub { font-size: 13px; color: var(--text-light); }
        
        .val-positive { color: var(--green); }
        .val-negative { color: var(--red); }
        
        /* Cores específicas dos cards */
        .card.corrente { border-top-color: #3182ce; }
        .card.capital { border-top-color: #ed8936; }
        .card.pessoal { border-top-color: #805ad5; }
        .card.investimento { border-top-color: #38a169; }
        
        .loading { text-align: center; padding: 50px; font-size: 18px; color: var(--text-light); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard Gerencial - Despesas</h1>
            <div class="filters">
                <label>Ano:</label>
                <select id="ano"><option value="2026" selected>2026</option><option value="2025">2025</option></select>
                <label>Tipo:</label>
                <select id="tipo"><option value="TRIMESTRE" selected>Trimestral</option></select>
                <label>Período:</label>
                <select id="valor"><option value="1">1º</option><option value="2">2º</option><option value="3" selected>3º</option><option value="4">4º</option></select>
                <button class="btn" onclick="carregarDados()">Atualizar Painel</button>
            </div>
        </div>

        <div id="painel" class="loading">Carregando dados...</div>
    </div>

    <script>
        function fmt(v) {
            if (v === undefined || v === null || isNaN(v)) return '0,00';
            return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function corVariacao(v) {
            if (v > 0) return 'val-negative'; // Despesa subir é ruim (vermelho)
            if (v < 0) return 'val-positive'; // Despesa descer é bom (verde)
            return '';
        }

        async function carregarDados() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo').value;
            const valor = document.getElementById('valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;

            const painel = document.getElementById('painel');
            painel.innerHTML = '<div class="loading">Buscando dados...</div>';

            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`);
                const data = await res.json();
                
                if (data.erro) {
                    painel.innerHTML = `<div class="loading" style="color:red;">${data.mensagem}</div>`;
                    return;
                }

                // --- FUNÇÃO AUXILIAR PARA BUSCAR GRUPOS ---
                const getGrupo = (lista, termo) => lista.find(g => g.nome.toUpperCase().includes(termo)) || {orcado:0, empenhado:0};
                
                const at = data.atual;
                const an = data.anterior;

                // 1. Mapeamento dos Grupos
                const aPessoal = getGrupo(at.grupos, 'PESSOAL');
                const aOutras = getGrupo(at.grupos, 'OUTRAS DESPESAS CORRENTES');
                const aJuros = getGrupo(at.grupos, 'JUROS');
                const aInvest = getGrupo(at.grupos, 'INVESTIMENTOS');
                const aInversoes = getGrupo(at.grupos, 'INVERSOES');
                const aAmort = getGrupo(at.grupos, 'AMORTIZACAO');

                const pPessoal = getGrupo(an.grupos, 'PESSOAL');
                const pOutras = getGrupo(an.grupos, 'OUTRAS DESPESAS CORRENTES');
                const pJuros = getGrupo(an.grupos, 'JUROS');
                const pInvest = getGrupo(an.grupos, 'INVESTIMENTOS');
                const pInversoes = getGrupo(an.grupos, 'INVERSOES');
                const pAmort = getGrupo(an.grupos, 'AMORTIZACAO');

                // 2. Cálculos de Despesas Correntes
                const aCorrenteOrc = aPessoal.orcado + aOutras.orcado + aJuros.orcado;
                const aCorrenteEmp = aPessoal.empenhado + aOutras.empenhado + aJuros.empenhado;
                const pCorrenteOrc = pPessoal.orcado + pOutras.orcado + pJuros.orcado;
                const pCorrenteEmp = pPessoal.empenhado + pOutras.empenhado + pJuros.empenhado;

                // 3. Cálculos de Despesas de Capital
                const aCapitalOrc = aInvest.orcado + aInversoes.orcado + aAmort.orcado;
                const aCapitalEmp = aInvest.empenhado + aInversoes.empenhado + aAmort.empenhado;
                const pCapitalOrc = pInvest.orcado + pInversoes.orcado + pAmort.orcado;
                const pCapitalEmp = pInvest.empenhado + pInversoes.empenhado + pAmort.empenhado;

                // --- FUNÇÃO PARA GERAR O BLOCO HTML ---
                const gerarBloco = (titulo, classeCard, orcAt, empAt, orcAn, empAn) => {
                    const varEmp = empAt - empAn;
                    const exec = orcAt > 0 ? (empAt / orcAt) * 100 : 0;
                    return `
                        <div class="section-title">${titulo}</div>
                        <div class="cards-grid">
                            <div class="card ${classeCard}">
                                <div class="card-title">Orçado</div>
                                <div class="card-value">R$ ${fmt(orcAt)}</div>
                                <div class="card-sub">Anterior: R$ ${fmt(orcAn)}</div>
                            </div>
                            <div class="card ${classeCard}">
                                <div class="card-title">Empenhado</div>
                                <div class="card-value">R$ ${fmt(empAt)}</div>
                                <div class="card-sub">Anterior: R$ ${fmt(empAn)}</div>
                            </div>
                            <div class="card ${classeCard}">
                                <div class="card-title">Variação Empenhada</div>
                                <div class="card-value ${corVariacao(varEmp)}">R$ ${fmt(varEmp)}</div>
                                <div class="card-sub">Frente ao ano anterior</div>
                            </div>
                            <div class="card ${classeCard}">
                                <div class="card-title">Execução Orçamentária</div>
                                <div class="card-value">${fmt(exec)}%</div>
                                <div class="card-sub">Do total orçado</div>
                            </div>
                        </div>
                    `;
                };

                // --- RENDERIZAÇÃO NA ORDEM EXATA ---
                let html = '';

                // 1. Correntes
                html += gerarBloco("1. Despesas Correntes (Pessoal + Outras + Juros)", "corrente", aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp);

                // 2. Capital
                html += gerarBloco("2. Despesas de Capital (Investimentos + Inversões + Amortização)", "capital", aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp);

                // 3. Pessoal
                html += gerarBloco("Pessoal e Encargos Sociais", "pessoal", aPessoal.orcado, aPessoal.empenhado, pPessoal.orcado, pPessoal.empenhado);

                // 4. Investimentos
                html += gerarBloco("Investimentos", "investimento", aInvest.orcado, aInvest.empenhado, pInvest.orcado, pInvest.empenhado);

                painel.innerHTML = html;

            } catch (e) {
                console.error(e);
                painel.innerHTML = '<div class="loading" style="color:red;">Erro ao conectar com o servidor.</div>';
            }
        }

        // Carrega automaticamente ao abrir a tela
        document.addEventListener('DOMContentLoaded', carregarDados);
    </script>
</body>
</html>"""

with open('dashboard_despesas.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Dashboard refeito com a ordem exata: 1. Correntes, 2. Capital, Pessoal e Investimentos.")
