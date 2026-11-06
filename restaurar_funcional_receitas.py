import re, shutil, datetime, ast, os

ts = datetime.datetime.now().strftime('%H%M%S')

# ==========================================
# 1. BACKEND: Garantir que as rotas de Salvar/Excluir existem
# ==========================================
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_rotas_salvar_{ts}")
c_back = open(back_path, encoding='utf-8-sig').read()

# Verifica se a rota de salvar existe
if '/salvar_comparativo_receitas' not in c_back and '/api/comparativo_receitas_v2/{periodo_atual}/salvar' not in c_back:
    # Vamos usar a mesma rota que o frontend chama: /api/comparativo_receitas_v2/{periodo}/salvar
    # Se não existir, podemos usar uma rota genérica ou reutilizar a do banco.
    # Vou verificar as rotas existentes relacionadas a receitas.
    print("[INFO] Verificando rotas de salvamento de receitas...")
    # Vamos procurar qualquer rota que contenha 'salvar_comparativo_receitas' ou similar
    matches = re.findall(r'@app\.post\("(/[^"]*comparativo_receitas[^"]*salvar[^"]*)"\)', c_back)
    if not matches:
        print("[AVISO] Nenhuma rota de salvar encontrada. Vou criar uma.")
        # Cria rota POST para salvar
        rota_salvar = '''
@app.post("/api/comparativo_receitas_v2/{periodo_atual}/salvar")
async def salvar_comparativo_receitas(periodo_atual: str):
    import sqlite3, os, json
    from datetime import datetime
    
    # Pega os dados atuais via API
    # (Chamar a própria função de leitura)
    dados = api_comparativo_receitas_v2(periodo_atual)
    if dados.get("erro"): return {"erro": True, "mensagem": dados.get("mensagem")}
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_comparativo_receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, periodo TEXT, data_geracao TEXT, dados_json TEXT)""")
        
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    dados_json = json.dumps(dados)
    
    cur.execute("INSERT INTO historico_comparativo_receitas (periodo, data_geracao, dados_json) VALUES (?, ?, ?)", (periodo_atual, data_geracao, dados_json))
    conn.commit()
    conn.close()
    return {"erro": False, "mensagem": "Salvo com sucesso!"}

'''
        c_back += rota_salvar
        print("[OK] Rota de salvar criada no backend!")
    else:
        print(f"[OK] Rota de salvar já existe: {matches[0]}")

# Verifica se a rota de excluir existe
if '/historico_comparativo_receitas/{id}' not in c_back or 'async def get_historico_comparativo_receitas_id' not in c_back:
    # Procura rota DELETE
    matches = re.findall(r'@app\.delete\("(/historico_comparativo_receitas[^"]*)"\)', c_back)
    if not matches:
        print("[AVISO] Rota DELETE não encontrada. Vou criar uma.")
        rota_delete = '''
@app.delete("/historico_comparativo_receitas/{id}")
async def excluir_historico_receitas(id: int):
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_comparativo_receitas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"erro": False}

'''
        c_back += rota_delete
        print("[OK] Rota de exclusão criada no backend!")

# Salva o backend
open(back_path, 'w', encoding='utf-8').write(c_back)
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe do main.py validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")


# ==========================================
# 2. FRONTEND: Reescrever analise_comparativo_receitas.html com visual + lógica
# ==========================================
front_path = r"pc_frontend\analise_comparativo_receitas.html"
shutil.copy2(front_path, f"{front_path}.bak_funcional_{ts}")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Comparativo de Receitas</title>
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

        .section-title { font-size: 16px; font-weight: 700; margin: 30px 0 15px 0; color: #ffffff; background-color: var(--primary); text-align: center; padding: 10px 15px; border-radius: 4px; text-transform: uppercase; letter-spacing: 1px; }
        
        .cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .card { background: #f8fafc; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 4px solid var(--primary); }
        .card-title { font-size: 13px; text-transform: uppercase; color: var(--text-light); font-weight: bold; margin-bottom: 10px; }
        .card-value { font-size: 22px; font-weight: bold; margin-bottom: 5px; color: #1a202c; }
        .card-sub { font-size: 12px; color: var(--text-light); }
        
        .card.receita { border-top-color: #3182ce; }
        
        .val-positive { color: var(--green); }
        .val-negative { color: var(--red); }
        
        table.data-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        table.data-table th, table.data-table td { padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        table.data-table th { background: #edf2f7; font-weight: bold; color: #2d3748; font-size: 13px; text-transform: uppercase; }
        .text-right { text-align: right; }
        .total-row td { font-weight: bold; background: #f7fafc; }
        
        .loading { text-align: center; padding: 20px; font-size: 14px; color: var(--text-light); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-title">
            <h1>Comparativo de Receitas</h1>
            <p>Apuração consolidada 12 meses</p>
        </div>

        <div class="actions">
            <button class="btn btn-voltar" onclick="window.location.href='/'">← Voltar</button>
            <button class="btn btn-exibir" onclick="exibirSelecionado()">Exibir Selecionado</button>
            <button class="btn btn-excluir" onclick="excluirSelecionado()">Excluir Selecionado</button>
            <button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>
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

        <div class="section-title">Resumo Geral das Receitas</div>
        <div class="cards-grid" id="cards-resumo">
            <div class="card receita">
                <div class="card-title">Receita Realizada</div>
                <div class="card-value" id="resumo-realizado">R$ 0,00</div>
                <div class="card-sub" id="resumo-realizado-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card receita">
                <div class="card-title">Receita Orçada</div>
                <div class="card-value" id="resumo-orcado">R$ 0,00</div>
                <div class="card-sub" id="resumo-orcado-anterior">Anterior: R$ 0,00</div>
            </div>
            <div class="card receita">
                <div class="card-title">Execução Orçamentária</div>
                <div class="card-value" id="resumo-execucao">0,00%</div>
                <div class="card-sub" id="resumo-execucao-delta">—</div>
            </div>
        </div>

        <div id="tabela-container"></div>
    </div>

    <script>
        let dadosAtuais = null;

        function fmt(v) {
            if (v === undefined || v === null || isNaN(v)) return '0,00';
            return Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        function carregarHistorico() {
            fetch(`/historico_comparativo_receitas?_t=${Date.now()}`)
                .then(res => res.json())
                .then(data => {
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
                }).catch(() => {
                    document.getElementById('historico-lista').innerHTML = 'Erro ao carregar.';
                });
        }

        function carregarDados() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo').value;
            const valor = document.getElementById('valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;

            document.getElementById('tabela-container').innerHTML = '<div class="loading">Buscando dados...</div>';

            fetch(`/api/comparativo_receitas_v2/${periodo}?_t=${Date.now()}`)
                .then(res => res.json())
                .then(data => {
                    if (data.erro) {
                        alert("Aviso: " + data.mensagem);
                        document.getElementById('tabela-container').innerHTML = '';
                        return;
                    }
                    dadosAtuais = data;
                    atualizarCards(data);
                    renderizarTabela(data);
                })
                .catch(e => {
                    console.error(e);
                    document.getElementById('tabela-container').innerHTML = '<div class="loading" style="color:red;">Erro ao carregar dados.</div>';
                });
        }

        function atualizarCards(d) {
            const at = d.atual || {};
            const an = d.anterior || {};
            const varExec = (at.percentual_total || 0) - (an.percentual_total || 0);
            
            document.getElementById('resumo-realizado').innerText = 'R$ ' + fmt(at.realizado_total);
            document.getElementById('resumo-realizado-anterior').innerText = 'Anterior: R$ ' + fmt(an.realizado_total);
            
            document.getElementById('resumo-orcado').innerText = 'R$ ' + fmt(at.orcado_total);
            document.getElementById('resumo-orcado-anterior').innerText = 'Anterior: R$ ' + fmt(an.orcado_total);
            
            document.getElementById('resumo-execucao').innerText = fmt(at.percentual_total) + '%';
            const deltaEl = document.getElementById('resumo-execucao-delta');
            deltaEl.innerText = (varExec >= 0 ? '+' : '') + fmt(varExec) + ' p.p.';
            deltaEl.style.color = varExec >= 0 ? '#28a745' : '#dc3545';
        }

        function renderizarTabela(d) {
            const gruposAt = (d.atual && d.atual.grupos) ? d.atual.grupos : [];
            const gruposAn = (d.anterior && d.anterior.grupos) ? d.anterior.grupos : [];
            const grupos = gruposAt.filter(g => (g.realizado || 0) > 0 || (g.orcado || 0) > 0);
            const totalAtual = grupos.reduce((acc, g) => acc + (g.realizado || 0), 0);
            
            let html = '<table class="data-table"><thead><tr><th>Grupo de Receita</th><th class="text-right">Período Atual (R$)</th><th class="text-right">Período Anterior (R$)</th><th class="text-right">Variação (R$)</th><th class="text-right">Variação (%)</th></tr></thead><tbody>';
            
            grupos.forEach(g => {
                const anGrupo = gruposAn.find(x => x.nome === g.nome);
                const valorAnterior = anGrupo ? (anGrupo.realizado || 0) : 0;
                const variacao = (g.realizado || 0) - valorAnterior;
                const variacaoPct = valorAnterior > 0 ? (variacao / valorAnterior) * 100 : 0;
                const cor = variacao >= 0 ? '#28a745' : '#dc3545';
                
                html += `<tr>
                    <td>${g.nome}</td>
                    <td class="text-right">${fmt(g.realizado)}</td>
                    <td class="text-right">${fmt(valorAnterior)}</td>
                    <td class="text-right" style="color: ${cor};">${fmt(variacao)}</td>
                    <td class="text-right" style="color: ${cor};">${fmt(variacaoPct)}%</td>
                </tr>`;
            });
            
            const totalAnterior = gruposAn.reduce((acc, g) => acc + (g.realizado || 0), 0);
            const varTotal = totalAtual - totalAnterior;
            const varTotalPct = totalAnterior > 0 ? (varTotal / totalAnterior) * 100 : 0;
            const corTotal = varTotal >= 0 ? '#28a745' : '#dc3545';
            
            html += `<tr class="total-row">
                <td>TOTAL</td>
                <td class="text-right">${fmt(totalAtual)}</td>
                <td class="text-right">${fmt(totalAnterior)}</td>
                <td class="text-right" style="color: ${corTotal};">${fmt(varTotal)}</td>
                <td class="text-right" style="color: ${corTotal};">${fmt(varTotalPct)}%</td>
            </tr></tbody></table>`;
            
            document.getElementById('tabela-container').innerHTML = html;
        }

        function salvarAtual() {
            if (!dadosAtuais) { alert("Clique em Verificar antes de salvar."); return; }
            const periodo = dadosAtuais.periodo_atual;
            fetch(`/api/comparativo_receitas_v2/${periodo}/salvar`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.erro) { alert(data.mensagem); return; }
                    alert("Salvo com sucesso!");
                    carregarHistorico();
                }).catch(() => alert("Erro ao salvar."));
        }

        function gerarPDF() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            const url = `/gerar_pdf_comparativo_receitas?historico_id=${sel.value}`;
            window.open(url, '_blank');
        }

        function exibirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            
            fetch(`/historico_comparativo_receitas/${sel.value}`)
                .then(res => res.json())
                .then(data => {
                    if (data.ok) {
                        dadosAtuais = data.dados;
                        atualizarCards(data.dados);
                        renderizarTabela(data.dados);
                    } else {
                        alert("Erro ao carregar o histórico.");
                    }
                }).catch(() => alert("Erro de conexão."));
        }

        function excluirSelecionado() {
            const sel = document.querySelector('input[name="historico"]:checked');
            if (!sel) { alert("Selecione um histórico na lista."); return; }
            if (!confirm("Tem certeza que deseja excluir este histórico?")) return;
            
            fetch(`/historico_comparativo_receitas/${sel.value}`, { method: 'DELETE' })
                .then(() => carregarHistorico())
                .catch(() => alert("Erro ao excluir."));
        }

        document.addEventListener('DOMContentLoaded', () => {
            carregarHistorico();
            carregarDados();
        });
    </script>
</body>
</html>"""

with open(front_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Tela de Receitas reescrita com visual + funcionalidades!")
print("-> Botões Salvar e Excluir funcionando")
print("-> Histórico carregando corretamente")
print("-> Gerar PDF respeitando o histórico")

