import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bp_estoques_bf_csv")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# ============================================================
# 1. Remove "Estoques" do item 2 (Análise BP)
# ============================================================
idx_bp = conteudo.find('elif nome_interno == "Análise BP":')
if idx_bp != -1:
    idx_fim_bp = conteudo.find('elif nome_interno ==', idx_bp + 10)
    if idx_fim_bp == -1:
        idx_fim_bp = conteudo.find('except Exception', idx_bp)
    
    bloco_bp = conteudo[idx_bp:idx_fim_bp]
    # Remove a linha que renderiza "estoques"
    bloco_bp = bloco_bp.replace(
        '''                        if k.lower() != 'estoques':''',
        '''                        # (linha de estoques removida)'''
    )
    # Se não houver o filtro, adiciona um
    if bloco_bp != conteudo[idx_bp:idx_fim_bp]:
        print("✅ Filtro de Estoques já existia e foi mantido.")
    else:
        # Adiciona filtro no loop de renderização do BP
        bloco_bp = bloco_bp.replace(
            '''                    for k, v in dados_bp.items():
                        if isinstance(v, dict):''',
            '''                    for k, v in dados_bp.items():
                        if isinstance(v, dict) and k.lower() != 'estoques':'''
        )
        print("✅ Linha 'Estoques' removida do item 2 (BP).")
    
    conteudo = conteudo[:idx_bp] + bloco_bp + conteudo[idx_fim_bp:]

# ============================================================
# 2. Reescreve o item 4 (BF) lendo o CSV
# ============================================================
idx_bf = conteudo.find('elif nome_interno == "Análise Financeira (BF)":')
if idx_bf != -1:
    idx_fim_bf = conteudo.find('elif nome_interno ==', idx_bf + 10)
    if idx_fim_bf == -1:
        idx_fim_bf = conteudo.find('except Exception', idx_bf)
    
    novo_bloco = '''elif nome_interno == "Análise Financeira (BF)":
                    import csv
                    import os
                    
                    # Procura o CSV do Balanço Financeiro
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    uploads_dir = os.path.join(base_dir, "..", "pc_storage", "uploads_raw")
                    csv_bf = None
                    
                    for nome_arquivo in os.listdir(uploads_dir):
                        if "BALANCO_FINANCEIRO" in nome_arquivo.upper() and periodo.replace("-", "_") in nome_arquivo.upper():
                            csv_bf = os.path.join(uploads_dir, nome_arquivo)
                            break
                    
                    if not csv_bf:
                        html_parts.append("<p style='color:red;'>CSV do Balanço Financeiro não encontrado para este período.</p>")
                    else:
                        linhas = []
                        with open(csv_bf, "r", encoding="latin-1") as f_csv:
                            leitor = csv.reader(f_csv, delimiter=';')
                            for linha in leitor:
                                linhas.append(linha)
                        
                        def limpar_valor(v):
                            if not v or not isinstance(v, str): return 0.0
                            limpo = v.replace('.', '').replace(',', '.').strip()
                            try: return float(limpo)
                            except: return 0.0
                        
                        def buscar_valor(linhas, termo, coluna_atual=1, coluna_anterior=2):
                            for linha in linhas:
                                if not linha: continue
                                for celula in linha:
                                    if termo.lower() in str(celula).lower():
                                        val_atual = limpar_valor(linha[coluna_atual]) if coluna_atual < len(linha) else 0.0
                                        val_ant = limpar_valor(linha[coluna_anterior]) if coluna_anterior < len(linha) else 0.0
                                        return val_atual, val_ant
                            return 0.0, 0.0
                        
                        # Receitas (colunas 1 e 2)
                        rec_orc_atual, rec_orc_ant = buscar_valor(linhas, "Receita Orçamentária", 1, 2)
                        rec_corrente_atual, rec_corrente_ant = buscar_valor(linhas, "RECEITAS CORRENTE", 1, 2)
                        rec_capital_atual, rec_capital_ant = buscar_valor(linhas, "RECEITAS DE CAPITAL", 1, 2)
                        rec_extra_atual, rec_extra_ant = buscar_valor(linhas, "Recebimentos Extraorçamentário", 1, 2)
                        saldo_ant_atual, saldo_ant_ant = buscar_valor(linhas, "Saldo em espécie do Exercício", 1, 2)
                        total_ing_atual, total_ing_ant = buscar_valor(linhas, "Total:", 1, 2)
                        
                        # Despesas (colunas 4 e 5)
                        desp_orc_atual, desp_orc_ant = buscar_valor(linhas, "Despesa Orçamentária", 4, 5)
                        desp_corrente_atual, desp_corrente_ant = buscar_valor(linhas, "CREDITO EMPENHADO LIQUIDADO PA", 4, 5)
                        desp_capital_atual, desp_capital_ant = buscar_valor(linhas, "INVESTIMENTOS", 4, 5)
                        desp_extra_atual, desp_extra_ant = buscar_valor(linhas, "Pagamentos Extraorçamentários", 4, 5)
                        saldo_seg_atual, saldo_seg_ant = buscar_valor(linhas, "Saldo em espécie para o Exercí", 4, 5)
                        total_disp_atual, total_disp_ant = buscar_valor(linhas, "Total:", 4, 5)
                        
                        html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Movimentação financeira consolidada.</p>")
                        html_parts.append("<table><thead><tr><th>INGRESSOS</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th><th>DISPÊNDIOS</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        
                        html_parts.append(f"<tr><td>Receita Orçamentária</td><td class='text-right'>{fmt(rec_orc_atual)}</td><td class='text-right'>{fmt(rec_orc_ant)}</td><td class='text-right'>{pct(calc_var(rec_orc_atual, rec_orc_ant))}</td><td>Despesa Orçamentária</td><td class='text-right'>{fmt(desp_orc_atual)}</td><td class='text-right'>{fmt(desp_orc_ant)}</td><td class='text-right'>{pct(calc_var(desp_orc_atual, desp_orc_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Receitas Correntes</td><td class='text-right'>{fmt(rec_corrente_atual)}</td><td class='text-right'>{fmt(rec_corrente_ant)}</td><td class='text-right'>{pct(calc_var(rec_corrente_atual, rec_corrente_ant))}</td><td>Despesas Correntes</td><td class='text-right'>{fmt(desp_corrente_atual)}</td><td class='text-right'>{fmt(desp_corrente_ant)}</td><td class='text-right'>{pct(calc_var(desp_corrente_atual, desp_corrente_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Receitas de Capital</td><td class='text-right'>{fmt(rec_capital_atual)}</td><td class='text-right'>{fmt(rec_capital_ant)}</td><td class='text-right'>{pct(calc_var(rec_capital_atual, rec_capital_ant))}</td><td>Despesas de Capital</td><td class='text-right'>{fmt(desp_capital_atual)}</td><td class='text-right'>{fmt(desp_capital_ant)}</td><td class='text-right'>{pct(calc_var(desp_capital_atual, desp_capital_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Recebimentos Extraorçamentários</td><td class='text-right'>{fmt(rec_extra_atual)}</td><td class='text-right'>{fmt(rec_extra_ant)}</td><td class='text-right'>{pct(calc_var(rec_extra_atual, rec_extra_ant))}</td><td>Pagamentos Extraorçamentários</td><td class='text-right'>{fmt(desp_extra_atual)}</td><td class='text-right'>{fmt(desp_extra_ant)}</td><td class='text-right'>{pct(calc_var(desp_extra_atual, desp_extra_ant))}</td></tr>")
                        html_parts.append(f"<tr><td>Saldo em Espécie do Exercício Anterior</td><td class='text-right'>{fmt(saldo_ant_atual)}</td><td class='text-right'>{fmt(saldo_ant_ant)}</td><td class='text-right'>{pct(calc_var(saldo_ant_atual, saldo_ant_ant))}</td><td>Saldo em Espécie para o Exercício Seguinte</td><td class='text-right'>{fmt(saldo_seg_atual)}</td><td class='text-right'>{fmt(saldo_seg_ant)}</td><td class='text-right'>{pct(calc_var(saldo_seg_atual, saldo_seg_ant))}</td></tr>")
                        html_parts.append(f"<tr><td><strong>Total Geral de Ingressos</strong></td><td class='text-right'><strong>{fmt(total_ing_atual)}</strong></td><td class='text-right'>{fmt(total_ing_ant)}</td><td class='text-right'>{pct(calc_var(total_ing_atual, total_ing_ant))}</td><td><strong>Total Geral de Dispêndios</strong></td><td class='text-right'><strong>{fmt(total_disp_atual)}</strong></td><td class='text-right'>{fmt(total_disp_ant)}</td><td class='text-right'>{pct(calc_var(total_disp_atual, total_disp_ant))}</td></tr>")
                        html_parts.append("</tbody></table>")
                        
                        # Texto dinâmico
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>")
                        html_parts.append(f"<li>Receita Orçamentária: {fmt(rec_orc_atual)} (variação {pct(calc_var(rec_orc_atual, rec_orc_ant))})</li>")
                        html_parts.append(f"<li>Despesa Orçamentária: {fmt(desp_orc_atual)} (variação {pct(calc_var(desp_orc_atual, desp_orc_ant))})</li>")
                        html_parts.append(f"<li>Recebimentos Extraorçamentários: {fmt(rec_extra_atual)} (variação {pct(calc_var(rec_extra_atual, rec_extra_ant))})</li>")
                        html_parts.append(f"<li>Pagamentos Extraorçamentários: {fmt(desp_extra_atual)} (variação {pct(calc_var(desp_extra_atual, desp_extra_ant))})</li>")
                        html_parts.append(f"<li>Saldo Final: {fmt(saldo_seg_atual)} (variação {pct(calc_var(saldo_seg_atual, saldo_seg_ant))})</li>")
                        html_parts.append("</ul>")
                        
                        # Gráfico de barras
                        labels = ["Rec. Orçamentária", "Desp. Orçamentária", "Receb. Extra", "Pag. Extra", "Saldo Anterior", "Saldo Seguinte"]
                        vals = [rec_orc_atual, desp_orc_atual, rec_extra_atual, desp_extra_atual, saldo_ant_atual, saldo_seg_atual]
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
    
    conteudo = conteudo[:idx_bf] + novo_bloco + conteudo[idx_fim_bf:]
    print("✅ Item 4 (BF) reescrito com a estrutura correta do CSV.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
