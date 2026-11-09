html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise por Centro de Custos - SGPC</title>
    <style>
        :root {
            --primary: #003366;
            --secondary: #00509e;
            --bg-light: #f4f7f6;
            --text-main: #2d3748;
            --border-color: #e2e8f0;
        }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-light); margin: 0; padding: 20px; color: var(--text-main); }
        .container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px; }
        .header h1 { color: var(--primary); margin: 0; font-size: 22px; }
        .header p { margin: 0; color: #666; font-size: 14px; }
        
        .toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; font-weight: 600; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block; }
        .btn-voltar { background-color: #ff8c00; color: white; }
        .btn-config { background-color: #6c757d; color: white; }
        .btn-verificar { background-color: #003366; color: white; }
        .btn-salvar { background-color: #28a745; color: white; }
        .btn-exibir { background-color: #17a2b8; color: white; }
        .btn-excluir { background-color: #dc3545; color: white; }
        .btn:hover { opacity: 0.9; }

        .historico-panel { background: #f9f9f9; border: 1px solid var(--border-color); border-radius: 5px; padding: 15px; margin-bottom: 20px; max-height: 200px; overflow-y: auto; }
        .historico-panel h3 { margin-top: 0; color: var(--primary); font-size: 16px; }
        .historico-item { display: block; padding: 8px; border-bottom: 1px solid #eee; cursor: pointer; }
        .historico-item:hover { background: #eef4f9; }
        .historico-item input { margin-right: 10px; }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border-color); }
        th { background-color: #eef4f9; color: var(--primary); font-weight: 600; }
        tr:hover { background-color: #f9f9f9; }
        .total-row td { font-weight: bold; background-color: #e6f0fa; }
        
        .loading { text-align: center; padding: 20px; color: #888; }
        .erro { color: #dc3545; padding: 20px; text-align: center; }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <div>
                <h1>Análise por Centro de Custos</h1>
                <p id="subtitle">Apuração consolidada 12 meses</p>
            </div>
        </div>

        <div class="toolbar">
            <a href="/analise_custo_pessoal" class="btn btn-voltar">← Voltar</a>
            <button class="btn btn-config" onclick="window.location.href='/configuracoes_custo_pessoal'">Configurações</button>
            <button class="btn btn-verificar" onclick="verificarAnalise()">Verificar Análise</button>
            <button class="btn btn-salvar" onclick="salvar()">Confirmar e Salvar</button>
            <button class="btn btn-exibir" onclick="exibirSelecionado()">Exibir Selecionado</button>
            <button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>
        </div>

        <div class="historico-panel">
            <h3>Histórico Salvo</h3>
            <div id="historico-lista" class="loading">Carregando histórico...</div>
        </div>

        <div id="tabela-container">
            <div class="loading">Carregando dados... Selecione um período e clique em "Verificar Análise".</div>
        </div>
    </div>

    <script>
        let dadosAtuais = null;

        function fmt(v) {
            return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        async function carregarHistorico() {
            try {
                const r = await fetch('/historico_centro_custos');
                const data = await r.json();
                const lista = document.getElementById('historico-lista');
                if (!data || data.length === 0) {
                    lista.innerHTML = '<div style="padding: 10px; color: #888;">Nenhum histórico.</div>';
                    return;
                }
                let html = '';
                data.forEach(item => {
                    html += '<label class="historico-item">';
                    html += '<input type="checkbox" class="check-historico" value="' + item.id + '"> ';
                    html += '<strong>' + item.periodo + '</strong> <span style="font-size: 11px; color: #888;">' + item.data_geracao + '</span>';
                    html += '</label>';
                });
                lista.innerHTML = html;
            } catch (e) {
                console.error(e);
                document.getElementById('historico-lista').innerHTML = '<div class="erro">Erro ao carregar histórico.</div>';
            }
        }

        async function verificarAnalise() {
            const periodo = '2026-TRIMESTRE-3';
            try {
                document.getElementById('tabela-container').innerHTML = '<div class="loading">Verificando dados...</div>';
                const r = await fetch(`/api/centro_custos/${periodo}?_t=${Date.now()}`, { cache: 'no-store' });
                const d = await r.json();
                if (d.erro) {
                    document.getElementById('tabela-container').innerHTML = '<div class="erro">' + d.mensagem + '</div>';
                    return;
                }
                dadosAtuais = d;
                renderizarTabela(d);
            } catch (e) {
                console.error(e);
                document.getElementById('tabela-container').innerHTML = '<div class="erro">Erro ao verificar a análise.</div>';
            }
        }

        function renderizarTabela(d) {
            let html = '<table>';
            html += '<thead><tr><th>Centro de Custo</th><th>Valor (R$)</th><th>% do Total</th></tr></thead>';
            html += '<tbody>';
            let total = 0;
            d.centros.forEach(c => { total += c.valor; });
            d.centros.forEach(c => {
                const pct = total > 0 ? (c.valor / total) * 100 : 0;
                html += `<tr><td>${c.nome}</td><td>${fmt(c.valor)}</td><td>${fmt(pct)}%</td></tr>`;
            });
            html += `<tr class="total-row"><td>TOTAL</td><td>${fmt(total)}</td><td>100%</td></tr>`;
            html += '</tbody></table>';
            document.getElementById('tabela-container').innerHTML = html;
        }

        async function salvar() {
            if (!dadosAtuais) { alert('Clique em "Verificar Análise" antes de salvar.'); return; }
            const r = await fetch('/salvar_centro_custos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ periodo: '2026-TRIMESTRE-3', dados: dadosAtuais })
            });
            const res = await r.json();
            if (res.ok) { alert('Salvo com sucesso!'); carregarHistorico(); }
            else { alert('Erro ao salvar: ' + res.mensagem); }
        }

        async function exibirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            const r = await fetch('/historico_centro_custos/' + check.value);
            const d = await r.json();
            if (d.dados) { dadosAtuais = d.dados; renderizarTabela(d.dados); }
        }

        async function excluirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert('Selecione um item no histórico.'); return; }
            if (!confirm('Deseja excluir este item?')) return;
            const r = await fetch('/historico_centro_custos/' + check.value, { method: 'DELETE' });
            const res = await r.json();
            if (res.ok) { alert('Excluído!'); carregarHistorico(); }
            else { alert('Erro ao excluir.'); }
        }

        document.addEventListener('DOMContentLoaded', () => {
            carregarHistorico();
            verificarAnalise();
        });
    </script>
</body>
</html>
"""

with open('../pc_frontend/analise_centro_custos.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[OK] Tela analise_centro_custos.html criada com sucesso!")
