import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_dfc_textos_grafico")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise DFC
idx_dfc = conteudo.find('elif nome_interno == "Análise DFC":')
if idx_dfc != -1:
    idx_fim_dfc = conteudo.find('elif nome_interno ==', idx_dfc + 10)
    if idx_fim_dfc == -1:
        idx_fim_dfc = conteudo.find('except Exception', idx_dfc)
    
    novo_bloco = '''elif nome_interno == "Análise DFC":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        return str(v).replace("R$", "").strip()
                    
                    dados_dfc = mod_dados.get("dados", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração do Fluxo de Caixa (método direto).</p>")
                    
                    # Textos dinâmicos de evolução
                    textos = []
                    
                    for tipo in ["operacional", "investimento", "financiamento"]:
                        if tipo in dados_dfc:
                            html_parts.append(f"<h3>Fluxo {tipo.title()}</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                            for k, v in dados_dfc[tipo].items():
                                if isinstance(v, dict):
                                    a = v.get("atual", 0)
                                    ant = v.get("anterior", 0)
                                    var = calc_var(a, ant)
                                    html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                    if abs(var) > 0.01:
                                        direcao = "positiva" if var > 0 else "negativa"
                                        textos.append(f"<li>Fluxo {tipo.title()} - {k.title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                            html_parts.append("</tbody></table>")
                    
                    # Apuração de Caixa
                    if "caixa" in dados_dfc:
                        html_parts.append("<h3>Apuração de Caixa</h3><table><thead><tr><th>ITEM</th><th>ATUAL</th><th>ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                        for k, v in dados_dfc["caixa"].items():
                            if isinstance(v, dict):
                                a = v.get("atual", 0)
                                ant = v.get("anterior", 0)
                                var = calc_var(a, ant)
                                html_parts.append(f"<tr><td>{k.title()}</td><td class='text-right'>{fmt_sem_rs(a)}</td><td class='text-right'>{fmt_sem_rs(ant)}</td><td class='text-right'>{pct(var)}</td></tr>")
                                if abs(var) > 0.01:
                                    direcao = "positiva" if var > 0 else "negativa"
                                    textos.append(f"<li>Apuração de Caixa - {k.title()}: variação {direcao} de {pct(var)} (de {fmt_sem_rs(ant)} para {fmt_sem_rs(a)}).</li>")
                        html_parts.append("</tbody></table>")
                    
                    # Textos de evolução
                    if textos:
                        html_parts.append("<h3>Evolução dos Fluxos de Caixa</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                    else:
                        html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os períodos.</p>")
                    
                    # Gráfico de barras
                    if "operacional" in dados_dfc:
                        labels = ["Ingressos Op.", "Desembolsos Op.", "Líquido Op.", "Ingressos Inv.", "Desembolsos Inv.", "Líquido Inv."]
                        vals = [
                            dados_dfc.get("operacional", {}).get("ingressos", {}).get("atual", 0),
                            dados_dfc.get("operacional", {}).get("desembolsos", {}).get("atual", 0),
                            dados_dfc.get("operacional", {}).get("liquido", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("ingressos", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("desembolsos", {}).get("atual", 0),
                            dados_dfc.get("investimento", {}).get("liquido", {}).get("atual", 0)
                        ]
                        html_parts.append("<div class='grafico'><canvas id='chartDFC'></canvas></div>")
                        html_parts.append("<script>")
                        html_parts.append("new Chart(document.getElementById('chartDFC'), {")
                        html_parts.append("type: 'bar',")
                        html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                        html_parts.append(f"{{ label: 'Valor (R$)', data: {json.dumps(vals)}, backgroundColor: ['#004b8d', '#dc3545', '#28a745', '#004b8d', '#dc3545', '#28a745'] }}")
                        html_parts.append("] },")
                        html_parts.append("options: { responsive: true, plugins: { legend: { display: false } } }")
                        html_parts.append("});")
                        html_parts.append("</script>")
                
                '''
    
    conteudo = conteudo[:idx_dfc] + novo_bloco + conteudo[idx_fim_dfc:]
    print("✅ Item 5 (DFC) ajustado: valores sem 'R$', textos dinâmicos e gráfico de barras.")
else:
    print("❌ Bloco da Análise DFC não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
