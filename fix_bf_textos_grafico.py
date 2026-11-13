import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bf_textos_grafico")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise Financeira (BF)
idx_bf = conteudo.find('elif nome_interno == "Análise Financeira (BF)":')
if idx_bf != -1:
    idx_fim = conteudo.find('elif nome_interno ==', idx_bf + 10)
    if idx_fim == -1:
        idx_fim = conteudo.find('except Exception', idx_bf)
    
    novo_bloco = '''elif nome_interno == "Análise Financeira (BF)":
                    atual = mod_dados.get("atual", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Movimentação financeira consolidada.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                    textos = []
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            a = v.get("atual", 0)
                            ant = v.get("anterior", 0)
                            var = calc_var(a, ant)
                            html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt(a)}</td><td class='text-right'>{fmt(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                            if abs(var) > 0.01:
                                direcao = "positiva" if var > 0 else "negativa"
                                textos.append(f"<li>{k.replace('_', ' ').title()}, variação {direcao} de {pct(var)} (de {fmt(ant)} para {fmt(a)}).</li>")
                    html_parts.append("</tbody></table>")
                    
                    # Textos dinâmicos
                    if textos:
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os períodos.</p>")
                    
                    # Gráfico de barras
                    labels = []
                    atual_vals = []
                    ant_vals = []
                    for k, v in atual.items():
                        if isinstance(v, dict):
                            labels.append(k.replace('_', ' ').title())
                            atual_vals.append(v.get("atual", 0))
                            ant_vals.append(v.get("anterior", 0))
                    
                    if labels:
                        html_parts.append("<div class='grafico'><canvas id='chartBF'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartBF'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                        html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                '''
    
    conteudo = conteudo[:idx_bf] + novo_bloco + conteudo[idx_fim:]
    print("✅ Textos dinâmicos e gráfico adicionados ao Balanço Financeiro (BF).")
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
