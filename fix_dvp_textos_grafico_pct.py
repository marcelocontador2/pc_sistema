import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_dvp_textos_grafico_pct")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise Patrimonial (DVP)
idx_dvp = conteudo.find('elif nome_interno == "Análise Patrimonial (DVP)":')
if idx_dvp != -1:
    idx_fim_dvp = conteudo.find('elif nome_interno ==', idx_dvp + 10)
    if idx_fim_dvp == -1:
        idx_fim_dvp = conteudo.find('except Exception', idx_dvp)
    
    novo_bloco = '''elif nome_interno == "Análise Patrimonial (DVP)":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração das Variações Patrimoniais.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                    
                    textos = []
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            atual = v.get("atual", 0)
                            anterior = v.get("anterior", 0)
                            var = calc_var(atual, anterior)
                            
                            # Caso especial para Margem Patrimonial (adiciona %)
                            if k == "margem_patrimonial":
                                html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{atual:.2f}%</td><td class='text-right'>{anterior:.2f}%</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>Margem Patrimonial: variação {direcao} de {pct(var)} (de {anterior:.2f}% para {atual:.2f}%).</li>")
                            else:
                                html_parts.append(f"<tr><td>{k.replace('_', ' ').title()}</td><td class='text-right'>{fmt_sem_rs(atual)}</td><td class='text-right'>{fmt_sem_rs(anterior)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>{k.replace('_', ' ').title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(anterior)} para {fmt_sem_rs(atual)}).</li>")
                    html_parts.append("</tbody></table>")
                    
                    # Textos de evolução
                    if textos:
                        html_parts.append("<h3>Evolução das Principais Contas</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os períodos.</p>")
                    
                    # Gráfico de barras
                    labels = []
                    atual_vals = []
                    ant_vals = []
                    for k, v in mod_dados.items():
                        if isinstance(v, dict):
                            labels.append(k.replace('_', ' ').title())
                            atual_vals.append(v.get("atual", 0))
                            ant_vals.append(v.get("anterior", 0))
                    
                    if labels:
                        html_parts.append("<div class='grafico'><canvas id='chartDVP'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartDVP'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                        html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                '''
    
    conteudo = conteudo[:idx_dvp] + novo_bloco + conteudo[idx_fim_dvp:]
    print("✅ Item 6 (DVP) ajustado: sem 'R$', com textos, gráfico e % na Margem Patrimonial.")
else:
    print("❌ Bloco da Análise Patrimonial não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
