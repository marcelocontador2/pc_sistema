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

        .section-title { font-size: 18px; font-weight: 600; margin: 30px 0 15px 0; color: var(--text); border-left: 4px solid var(--primary); padding-left: 10px; }
        
        .cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .card { background: var(--card-bg); border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid var(--primary); }
        .card-title { font-size: 13px; text-transform: uppercase; color: var(--text-light); font-weight: bold; margin-bottom: 10px; }
        .card-value { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .card-sub { font-size: 13px; color: var(--text-light); }
        
        .val-positive { color: var(--green); }
        .val-negative { color: var(--red); }
        
        /* Cores específicas dos cards */
        .card.corrente { border-top-color: #3182ce; }
        .card.pessoal { border-top-color: #805ad5; }
        
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

                // --- CÁLCULOS MATEMÁTICOS ---
                const at = data.atual;
                const an = data.anterior;

                // 1. Achar grupos
                const aPessoal = at.grupos.find(g => g.nome.includes('PESSOAL')) || {orcado:0, empenhado:0};
                const aOutras = at.grupos.find(g => g.nome.includes('OUTRAS DESPESAS CORRENTES')) || {orcado:0, empenhado:0};
                const aJuros = at.grupos.find(g => g.nome.includes('JUROS')) || {orcado:0, empenhado:0};

                const pPessoal = an.grupos.find(g => g.nome.includes('PESSOAL')) || {orcado:0, empenhado:0};
                const pOutras = an.grupos.find(g => g.nome.includes('OUTRAS DESPESAS CORRENTES')) || {orcado:0, empenhado:0};
                const pJuros = an.grupos.find(g => g.nome.includes('JUROS')) || {orcado:0, empenhado:0};

                // 2. Consolidar Despesas Correntes (Pessoal + Outras + Juros)
                const aCorrenteOrc = aPessoal.orcado + aOutras.orcado + aJuros.orcado;
                const aCorrenteEmp = aPessoal.empenhado + aOutras.empenhado + aJuros.empenhado;
                
                const pCorrenteOrc = pPessoal.orcado + pOutras.orcado + pJuros.orcado;
                const pCorrenteEmp = pPessoal.empenhado + pOutras.empenhado + pJuros.empenhado;

                // 3. Variações
                const varCorrenteEmp = aCorrenteEmp - pCorrenteEmp;
                const varPessoalEmp = aPessoal.empenhado - pPessoal.empenhado;

                // 4. Percentuais de Execução
                const execCorrente = aCorrenteOrc > 0 ? (aCorrenteEmp / aCorrenteOrc) * 100 : 0;
                const execPessoal = aPessoal.orcado > 0 ? (aPessoal.empenhado / aPessoal.orcado) * 100 : 0;

                // --- RENDERIZAÇÃO ---
                let html = '';

                // BLOCO 1: DESPESAS CORRENTES
                html += `<div class="section-title">Despesas Correntes (Pessoal + Outras + Juros)</div>`;
                html += `<div class="cards-grid">
                    <div class="card corrente">
                        <div class="card-title">Orçado</div>
                        <div class="card-value">R$ ${fmt(aCorrenteOrc)}</div>
                        <div class="card-sub">Anterior: R$ ${fmt(pCorrenteOrc)}</div>
                    </div>
                    <div class="card corrente">
                        <div class="card-title">Empenhado</div>
                        <div class="card-value">R$ ${fmt(aCorrenteEmp)}</div>
                        <div class="card-sub">Anterior: R$ ${fmt(pCorrenteEmp)}</div>
                    </div>
                    <div class="card corrente">
                        <div class="card-title">Variação Empenhada</div>
                        <div class="card-value ${corVariacao(varCorrenteEmp)}">R$ ${fmt(varCorrenteEmp)}</div>
                        <div class="card-sub">Frente ao ano anterior</div>
                    </div>
                    <div class="card corrente">
                        <div class="card-title">Execução Orçamentária</div>
                        <div class="card-value">${fmt(execCorrente)}%</div>
                        <div class="card-sub">Do total orçado</div>
                    </div>
                </div>`;

                // BLOCO 2: PESSOAL E ENCARGOS
                html += `<div class="section-title">Pessoal e Encargos Sociais</div>`;
                html += `<div class="cards-grid">
                    <div class="card pessoal">
                        <div class="card-title">Orçado</div>
                        <div class="card-value">R$ ${fmt(aPessoal.orcado)}</div>
                        <div class="card-sub">Anterior: R$ ${fmt(pPessoal.orcado)}</div>
                    </div>
                    <div class="card pessoal">
                        <div class="card-title">Empenhado</div>
                        <div class="card-value">R$ ${fmt(aPessoal.empenhado)}</div>
                        <div class="card-sub">Anterior: R$ ${fmt(pPessoal.empenhado)}</div>
                    </div>
                    <div class="card pessoal">
                        <div class="card-title">Variação Empenhada</div>
                        <div class="card-value ${corVariacao(varPessoalEmp)}">R$ ${fmt(varPessoalEmp)}</div>
                        <div class="card-sub">Frente ao ano anterior</div>
                    </div>
                    <div class="card pessoal">
                        <div class="card-title">Execução Orçamentária</div>
                        <div class="card-value">${fmt(execPessoal)}%</div>
                        <div class="card-sub">Do total orçado</div>
                    </div>
                </div>`;

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

print("[OK] Dashboard de alto nível criado com sucesso (dashboard_despesas.html)!")
