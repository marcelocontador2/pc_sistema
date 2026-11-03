html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Comparativo de Despesas</title>
    <style>
        :root {
            --primary: #2b6cb0;
            --bg: #f4f6f9;
            --card-bg: #ffffff;
            --text: #2d3748;
            --text-light: #718096;
            --green: #38a169;
            --red: #e53e3e;
        }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--text); }
        .container { max-width: 1200px; margin: 0 auto; background: var(--card-bg); padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        
        .header-title h1 { margin: 0 0 5px 0; font-size: 24px; color: #1a202c; }
        .header-title p { margin: 0 0 20px 0; color: var(--text-light); font-size: 14px; }

        .actions { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; color: #fff; font-weight: bold; font-size: 14px; }
        .btn-voltar { background: #ed8936; }
        .btn-exibir { background: #38a169; }
        .btn-excluir { background: #e53e3e; }
        .btn-pdf { background: #3182ce; }
        .btn-salvar { background: #38a169; }
        .btn-verificar { background: #3182ce; }
        .btn:hover { opacity: 0.9; }

        .historico-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin-bottom: 20px; }
        .historico-box h3 { font-size: 14px; color: #4a5568; margin-bottom: 10px; text-transform: uppercase; margin-top: 0;}
        .historico-box ul { list-style: none; padding: 0; margin: 0; }
        .historico-box li { padding: 8px 0; border-bottom: 1px solid #edf2f7; font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .historico-box li:last-child { border-bottom: none; }

        .filters { display: flex; gap: 10px; align-items: center; background: #f7fafc; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .filters label { font-size: 14px; font-weight: 600; }
        .filters select { padding: 6px; border: 1px solid #cbd5e0; border-radius: 4px; font-size: 14px; }

        .section-title { font-size: 18px; font-weight: 700; margin: 30px 0 15px 0; color: var(--text); text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; text-transform: uppercase; }
        .cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .card { background: #f8fafc; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 4px solid var(--primary); }
        .card-title { font-size: 13px; text-transform: uppercase; color: var(--text-light); font-weight: bold; margin-bottom: 10px; }
        .card-value { font-size: 22px; font-weight: bold; margin-bottom: 5px; color: #1a202c; }
        .card-sub { font-size: 12px; color: var(--text-light); }
        
        .val-positive { color: var(--green); }
        .val-negative { color: var(--red); }
        
        .card.corrente { border-top-color: #3182ce; }
        .card.capital { border-top-color: #ed8936; }
        .card.total-geral { border-top-color: #2d3748; background-color: #edf2f7; }
        
        .loading { text-align: center; padding: 20px; font-size: 14px; color: var(--text-light); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-title">
            <h1>Comparativo de Despesas</h1>
            <p>Apuração consolidada 12 meses</p>
        </div>

        <div class="actions">
            <button class="btn btn-voltar" onclick="window.location.href='/'">← Voltar</button>
            <button class="btn btn-exibir" onclick="exibirSelecionado()">Exibir Selecionado</button>
            <button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>
            <button class="btn btn-pdf" onclick="window.print()">Gerar PDF</button>
            <button class="btn btn-salvar" onclick="salvarAtual()">Confirmar e Salvar</button>
        </div>

        <div class="historico-box">
            <h3>Histórico Salvo</h3>
            <div id="historico-lista" class="loading">Carregando histórico...</div>
        </div>

        <div class="filters">
            <label>Ano:</label>
            <select id="ano"><option value="2026" selected>2026</option><option value="2025">2025</option></select>
            <label>Tipo:</label>
            <select id="tipo"><option value="TRIMESTRE" selected>Trimestral</option><option value="MES">Mensal</option></select>
            <label>Período:</label>
            <select id="valor"><option value="1">1º</option><option value="2">2º</option><option value="3" selected>3º</option><option value="4">4º</option></select>
            <button class="btn btn-verificar" onclick="carregarDados()">Verificar</button>
        </div>

        <div id="painel-cards"></div>
    </div>

    <script>
        let dadosAtuais = null;

        function fmt(v) {
            if (v === undefined || v === null || isNaN(v)) return '0,00';
            return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function corVariacao(v) {
            if (v > 0) return 'val-negative'; 
            if (v < 0) return 'val-positive'; 
            return '';
        }

        function renderizarCards(data) {
            const painel = document.getElementById('painel-cards');
            
            if (!data || data.erro) {
                painel.innerHTML = `<div class="loading" style="color:red;">${data ? data.mensagem : 'Erro ao carregar dados.'}</div>`;
                return;
            }

            const getGrupo = (lista, termo) => lista.find(g => g.nome.toUpperCase().includes(termo)) || {orcado:0, empenhado:0};
            
            const at = data.atual;
            const an = data.anterior;

            // Mapeamento
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

            // Cálculos
            const aCorrenteOrc = aPessoal.orcado + aOutras.orcado + aJuros.orcado;
            const aCorrenteEmp = aPessoal.empenhado + aOutras.empenhado + aJuros.empenhado;
            const pCorrenteOrc = pPessoal.orcado + pOutras.orcado + pJuros.orcado;
            const pCorrenteEmp = pPessoal.empenhado + pOutras.empenhado + pJuros.empenhado;

            const aCapitalOrc = aInvest.orcado + aInversoes.orcado + aAmort.orcado;
            const aCapitalEmp = aInvest.empenhado + aInversoes.empenhado + aAmort.empenhado;
            const pCapitalOrc = pInvest.orcado + pInversoes.orcado + pAmort.orcado;
            const pCapitalEmp = pInvest.empenhado + pInversoes.empenhado + pAmort.empenhado;

            const aTotalOrc = aCorrenteOrc + aCapitalOrc;
            const aTotalEmp = aCorrenteEmp + aCapitalEmp;
            const pTotalOrc = pCorrenteOrc + pCapitalOrc;
            const pTotalEmp = pCorrenteEmp + pCapitalEmp;

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

            let html = '';
            html += gerarBloco("1. Despesas Correntes (Pessoal + Outras + Juros)", "corrente", aCorrenteOrc, aCorrenteEmp, pCorrenteOrc, pCorrenteEmp);
            html += gerarBloco("2. Despesas de Capital (Investimentos + Inversões)", "capital", aCapitalOrc, aCapitalEmp, pCapitalOrc, pCapitalEmp);
            html += gerarBloco("TOTAL GERAL DAS DESPESAS (Correntes + Capital)", "total-geral", aTotalOrc, aTotalEmp, pTotalOrc, pTotalEmp);

            painel.innerHTML = html;
        }

        async function carregarDados() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo').value;
            const valor = document.getElementById('valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;

            document.getElementById('painel-cards').innerHTML = '<div class="loading">Buscando dados...</div>';

            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodo}?_t=${Date.now()}`);
                const data = await res.json();
                dadosAtuais = data; // Salva na memória para o botão Salvar
                renderizarCards(data);
            } catch (e) {
                console.error(e);
                document.getElementById('painel-cards').innerHTML = '<div class="loading" style="color:red;">Erro de conexão.</div>';
            }
        }

        async function salvarAtual() {
            if (!dadosAtuais || dadosAtuais.erro) { alert("Clique em Verificar antes de salvar."); return; }
            const periodo = dadosAtuais.periodo_atual;
            try {
                const res = await fetch(`/api/comparativo_despesas_v2/${periodo}/salvar`, { method: 'POST' });
                const data = await res.json();
                if (data.erro) { alert(data.mensagem); return; }
                alert("Salvo com sucesso!");
                carregarHistorico();
            } catch (e) {
                alert("Erro ao salvar.");
            }
        }

        async function carregarHistorico() {
            try {
                const res = await fetch(`/historico_comparativo_despesas?_t=${Date.now()}`);
                const data = await res.json();
                const div = document.getElementById('historico-lista');
                if (data.length === 0) {
                    div.innerHTML = '<p style="color:#718096;font-size:13px;">Nenhum histórico.</p>';
                    return;
                }
                let html = '<ul>';
                data.forEach(item => {
                    html += `<li>
                        <input type="radio" name="historico" value="${item.id}">
                        <span><b>Período:</b> ${item.periodo} | <b>Gerado em:</b> ${item.data_geracao}</span>
                    </li>`;
                });
                html += '</ul>';
                div.innerHTML = html;
            } catch (e) {
                document.getElementById('historico-lista').innerHTML = 'Erro ao carregar.';
            }
        }

        async function exibirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            
            try {
                const res = await fetch(`/historico_comparativo_despesas/${sel.value}`);
                const data = await res.json();
                if (data.ok) {
                    dadosAtuais = data.dados;
                    renderizarCards(data.dados);
                } else {
                    alert("Erro ao carregar o histórico.");
                }
            } catch (e) {
                alert("Erro de conexão.");
            }
        }

        async function excluirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            if (!confirm("Tem certeza que deseja excluir este histórico?")) return;
            
            try {
                await fetch(`/historico_comparativo_despesas/${sel.value}`, { method: 'DELETE' });
                carregarHistorico();
            } catch (e) {
                alert("Erro ao excluir.");
            }
        }

        // Inicialização
        document.addEventListener('DOMContentLoaded', () => {
            carregarHistorico();
            carregarDados(); // Já carrega os dados visuais ao abrir a tela
        });
    </script>
</body>
</html>"""

with open('analise_comparativo_despesas.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Tela unificada criada: Cards do Dashboard + Regra de Negócio do Histórico!")
