import shutil
import ast
import re

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_item8_padrao_imagem")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o início e o fim do bloco "Comparativo de Receitas"
idx_ini = conteudo.find('elif nome_interno == "Comparativo de Receitas":')
if idx_ini == -1:
    print("❌ Bloco do Item 8 não encontrado.")
    raise SystemExit(1)

idx_fim = conteudo.find('elif nome_interno == "Comparativo de Despesas":', idx_ini)
if idx_fim == -1:
    print("❌ Fim do bloco do Item 8 não encontrado.")
    raise SystemExit(1)

novo_bloco = '''elif nome_interno == "Comparativo de Receitas":
                    atual = mod_dados.get("atual", {})
                    anterior = mod_dados.get("anterior", {})
                    periodo_atual = mod_dados.get("periodo_atual", "")
                    periodo_anterior = mod_dados.get("periodo_anterior", "")
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo consolidado de receitas.</p>")
                    
                    # ---- 1. TABELA DE INDICADORES ----
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>VALOR</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Orçada</td><td class='text-right'>{fmt(atual.get('orcado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt(atual.get('realizado_total'))}</td></tr>")
                    html_parts.append(f"<tr><td>% Execução</td><td class='text-right'>{atual.get('percentual_total', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 2. COMPOSIÇÃO POR GRUPO ----
                    html_parts.append("<h3>Composição por Grupo</h3>")
                    html_parts.append("<table><thead><tr><th>GRUPO</th><th>ORÇADO</th><th>REALIZADO</th><th>%</th></tr></thead><tbody>")
                    for g in atual.get("grupos", []):
                        html_parts.append(f"<tr><td>{g.get('nome','')}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('orcado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{fmt(g.get('realizado'))}</td>")
                        html_parts.append(f"<td class='text-right'>{g.get('percentual', 0):.2f}%</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # ---- 3. TEXTOS DINÂMICOS ----
                    textos = []
                    orc_tot = atual.get("orcado_total", 0) or 0
                    real_tot = atual.get("realizado_total", 0) or 0
                    pct_tot = atual.get("percentual_total", 0) or 0
                    if orc_tot > 0:
                        if pct_tot >= 100:
                            textos.append(f"<li>A receita realizada de {fmt(real_tot)} superou a orçada de {fmt(orc_tot)} em {pct_tot - 100:.2f}% (execução de {pct_tot:.2f}%).</li>")
                        else:
                            textos.append(f"<li>A receita realizada de {fmt(real_tot)} ficou abaixo da orçada de {fmt(orc_tot)}, com execução de {pct_tot:.2f}%.</li>")
                    else:
                        textos.append(f"<li>Não há receita orçada cadastrada para o período; a receita realizada foi de {fmt(real_tot)}.</li>")
                    
                    for g in atual.get("grupos", []):
                        nome = g.get('nome', '')
                        orc = g.get('orcado', 0) or 0
                        real = g.get('realizado', 0) or 0
                        pct_g = g.get('percentual', 0) or 0
                        if orc > 0 and real > 0:
                            if pct_g >= 100:
                                textos.append(f"<li>{nome}: arrecadação de {fmt(real)} ({pct_g:.2f}% do orçado de {fmt(orc)}).</li>")
                            elif real > 0:
                                textos.append(f"<li>{nome}: arrecadação de {fmt(real)}, abaixo do orçado de {fmt(orc)} ({pct_g:.2f}%).</li>")
                        elif real > 0:
                            textos.append(f"<li>{nome}: arrecadação de {fmt(real)} sem previsão orçada.</li>")
                    
                    if textos:
                        html_parts.append("<h3>Análise de Execução</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os períodos.</p>")
                    
                    # ---- 4. GRÁFICO DE BARRAS (Orçado x Realizado por grupo) ----
                    grupos = atual.get("grupos", [])
                    if grupos:
                        labels = [g.get('nome','') for g in grupos]
                        vals_orc = [g.get('orcado', 0) or 0 for g in grupos]
                        vals_real = [g.get('realizado', 0) or 0 for g in grupos]
                        html_parts.append("<div class='grafico' style='max-width: 500px; height: 220px; margin: 10px auto;'><canvas id='chartReceitasBarras' style='width:100%; height:100%;'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartReceitasBarras'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [")
                        html_parts.append(f"{{ label: 'Orçado', data: {json.dumps(vals_orc)}, backgroundColor: '#6c757d' }},")
                        html_parts.append(f"{{ label: 'Realizado', data: {json.dumps(vals_real)}, backgroundColor: '#004b8d' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { x: { ticks: { font: { size: 7 } } }, y: { ticks: { font: { size: 7 } } } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                '''

conteudo = conteudo[:idx_ini] + novo_bloco + conteudo[idx_fim:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
    print("✅ Item 8 (Comparativo de Receitas) refeito no padrão da imagem: tabelas azuis, textos dinâmicos e gráfico de barras.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
