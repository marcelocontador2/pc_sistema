import re, shutil, datetime

arquivo = 'analise_comparativo_receitas.html'
shutil.copy2(arquivo, f"{arquivo}.bak_{datetime.datetime.now().strftime('%H%M%S')}")
c = open(arquivo, encoding='utf-8').read()

# 1. Extrair o bloco <script> intacto (para não perder a lógica de dados)
script_match = re.search(r'(<script>.*?</script>)', c, re.DOTALL)
script_original = script_match.group(1) if script_match else ""

# 2. Criar o novo HTML com o visual padrão das Despesas
novo_html = """<!DOCTYPE html>
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
        
        /* Grid de 3 colunas para as Receitas */
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

    <!-- O script original da tela de receitas é inserido aqui intacto -->
    SCRIPT_PLACEHOLDER
</body>
</html>"""

# 3. Inserir o script original de volta
novo_html = novo_html.replace('SCRIPT_PLACEHOLDER', script_original)

# 4. Salvar o arquivo
open(arquivo, 'w', encoding='utf-8').write(novo_html)
print("[OK] Visual da tela de Receitas padronizado com o dashboard de Despesas!")
