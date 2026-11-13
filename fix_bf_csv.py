import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bf_csv")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise Financeira (BF)
idx_bf = conteudo.find('elif nome_interno == "Análise Financeira (BF)":')
if idx_bf != -1:
    idx_fim = conteudo.find('elif nome_interno ==', idx_bf + 10)
    if idx_fim == -1:
        idx_fim = conteudo.find('except Exception', idx_bf)
    
    novo_bloco = '''elif nome_interno == "Análise Financeira (BF)":
                    # Lê o CSV do Balanço Financeiro
                    import csv
                    import os
                    from datetime import datetime
                    
                    csv_bf = None
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    uploads_dir = os.path.join(base_dir, "..", "pc_storage", "uploads_raw")
                    
                    # Procura o CSV do período
                    for nome_arquivo in os.listdir(uploads_dir):
                        if "BALANCO_FINANCEIRO" in nome_arquivo.upper() and periodo.replace("-", "_") in nome_arquivo.upper():
                            csv_bf = os.path.join(uploads_dir, nome_arquivo)
                            break
                    
                    if not csv_bf:
                        html_parts.append("<p style='color:red;'>CSV do Balanço Financeiro não encontrado para este período.</p>")
                    else:
                        # Lê o CSV
                        linhas = []
                        with open(csv_bf, "r", encoding="latin-1") as f_csv:
                            leitor = csv.reader(f_csv, delimiter=';')
                            for linha in leitor:
                                linhas.append(linha)
                        
                        # Função para limpar valores
                        def limpar_valor(v):
                            if not v or not isinstance(v, str): return 0.0
                            limpo = v.replace('.', '').replace(',', '.').strip()
                            try: return float(limpo)
                            except: return 0.0
                        
                        # Extrai os valores das linhas
                        # Estrutura do CSV: INGRESSOS | DISPÊNDIOS | Receita Orçamentária | ...
                        def buscar_valor(linhas, termo, coluna=1):
                            for linha in linhas:
                                if not linha: continue
                                for i, celula in enumerate(linha):
                                    if termo.lower() in str(celula).lower():
                                        if i + coluna < len(linha):
                                            return limpar_valor(linha[i + coluna])
                            return 0.0
                        
                        # Valores principais (atual)
                        receita_orcamentaria = buscar_valor(linhas, "Receita Orçamentária")
                        despesa_orcamentaria = buscar_valor(linhas, "Despesa Orçamentária", 4)
                        recebimentos_extra = buscar_valor(linhas, "Recebimentos Extraorçamentários")
                        pagamentos_extra = buscar_valor(linhas, "Pagamentos Extraorçamentários", 4)
                        saldo_anterior = buscar_valor(linhas, "Saldo em Espécie do Exercício Anterior")
                        saldo_seguinte = buscar_valor(linhas, "Saldo em Espécie para o Exercício Seguinte")
                        total_ingressos = receita_orcamentaria + recebimentos_extra + saldo_anterior
                        total_dispendios = despesa_orcamentaria + pagamentos_extra + saldo_seguinte
                        
                        html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Movimentação financeira consolidada.</p>")
                        html_parts.append("<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        html_parts.append(f"<tr><td>Receita Orçamentária</td><td class='text-right'>{fmt(receita_orcamentaria)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td>Despesa Orçamentária</td><td class='text-right'>{fmt(despesa_orcamentaria)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td>Recebimentos Extraorçamentários</td><td class='text-right'>{fmt(recebimentos_extra)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td>Pagamentos Extraorçamentários</td><td class='text-right'>{fmt(pagamentos_extra)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td>Saldo em Espécie do Exercício Anterior</td><td class='text-right'>{fmt(saldo_anterior)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td>Saldo em Espécie para o Exercício Seguinte</td><td class='text-right'>{fmt(saldo_seguinte)}</td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td><strong>Total Geral de Ingressos</strong></td><td class='text-right'><strong>{fmt(total_ingressos)}</strong></td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append(f"<tr><td><strong>Total Geral de Dispêndios</strong></td><td class='text-right'><strong>{fmt(total_dispendios)}</strong></td><td class='text-right'>-</td><td class='text-right'>-</td></tr>")
                        html_parts.append("</tbody></table>")
                        
                        # Texto dinâmico
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>")
                        html_parts.append(f"<li>Receita Orçamentária: {fmt(receita_orcamentaria)}</li>")
                        html_parts.append(f"<li>Despesa Orçamentária: {fmt(despesa_orcamentaria)}</li>")
                        html_parts.append(f"<li>Recebimentos Extraorçamentários: {fmt(recebimentos_extra)}</li>")
                        html_parts.append(f"<li>Pagamentos Extraorçamentários: {fmt(pagamentos_extra)}</li>")
                        html_parts.append(f"<li>Saldo Final: {fmt(saldo_seguinte)}</li>")
                        html_parts.append("</ul>")
                        
                        # Gráfico de barras
                        labels = ["Rec. Orçamentária", "Desp. Orçamentária", "Receb. Extra", "Pag. Extra", "Saldo Anterior", "Saldo Seguinte"]
                        vals = [receita_orcamentaria, despesa_orcamentaria, recebimentos_extra, pagamentos_extra, saldo_anterior, saldo_seguinte]
                        html_parts.append("<div class='grafico'><canvas id='chartBF'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartBF'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Valor (R$)', data: {json.dumps(vals)}, backgroundColor: ['#004b8d', '#dc3545', '#28a745', '#fd7e14', '#6c757d', '#17a2b8'] }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, plugins: { legend: { display: false } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                '''
    
    conteudo = conteudo[:idx_bf] + novo_bloco + conteudo[idx_fim:]
    print("✅ Item 4 (BF) ajustado para ler o CSV do Balanço Financeiro.")
else:
    print("❌ Bloco da Análise Financeira não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
