import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_bo_grafico")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco da Análise Orçamentária (BO)
idx_bo = conteudo.find('elif nome_interno == "Análise Orçamentária (BO)":')
if idx_bo != -1:
    # Encontra o final do bloco (próximo elif)
    idx_fim = conteudo.find('elif nome_interno ==', idx_bo + 10)
    if idx_fim == -1:
        idx_fim = conteudo.find('except Exception', idx_bo)
    
    novo_bloco = '''elif nome_interno == "Análise Orçamentária (BO)":
                    atual = mod_dados.get("atual", {})
                    anterior = mod_dados.get("anterior", {})
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Comparativo das receitas e despesas orçamentárias.</p>")
                    html_parts.append("<table><thead><tr><th>INDICADOR</th><th>PERÍODO ATUAL</th><th>PERÍODO ANTERIOR</th><th>VAR. (%)</th></tr></thead><tbody>")
                    html_parts.append(f"<tr><td>Receita Realizada</td><td class='text-right'>{fmt(atual.get('receita_realizada'))}</td><td class='text-right'>{fmt(anterior.get('receita_realizada'))}</td><td class='text-right'>{pct(calc_var(atual.get('receita_realizada',0), anterior.get('receita_realizada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Empenhada</td><td class='text-right'>{fmt(atual.get('despesa_empenhada'))}</td><td class='text-right'>{fmt(anterior.get('despesa_empenhada'))}</td><td class='text-right'>{pct(calc_var(atual.get('despesa_empenhada',0), anterior.get('despesa_empenhada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Superávit/Déficit</td><td class='text-right'>{fmt(atual.get('superavit'))}</td><td class='text-right'>{fmt(anterior.get('superavit'))}</td><td class='text-right'>{pct(calc_var(atual.get('superavit',0), anterior.get('superavit',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Restos a Pagar</td><td class='text-right'>{fmt(atual.get('restos_pagar'))}</td><td class='text-right'>{fmt(anterior.get('restos_pagar'))}</td><td class='text-right'>{pct(calc_var(atual.get('restos_pagar',0), anterior.get('restos_pagar',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Receita Orçada</td><td class='text-right'>{fmt(atual.get('receita_orcada'))}</td><td class='text-right'>{fmt(anterior.get('receita_orcada'))}</td><td class='text-right'>{pct(calc_var(atual.get('receita_orcada',0), anterior.get('receita_orcada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>Despesa Orçada</td><td class='text-right'>{fmt(atual.get('despesa_orcada'))}</td><td class='text-right'>{fmt(anterior.get('despesa_orcada'))}</td><td class='text-right'>{pct(calc_var(atual.get('despesa_orcada',0), anterior.get('despesa_orcada',0)))}</td></tr>")
                    html_parts.append(f"<tr><td>% Realização Receitas</td><td class='text-right'>{atual.get('pct_receita', 0):.2f}%</td><td class='text-right'>{anterior.get('pct_receita', 0):.2f}%</td><td class='text-right'>-</td></tr>")
                    html_parts.append(f"<tr><td>% Realização Despesas</td><td class='text-right'>{atual.get('pct_despesa', 0):.2f}%</td><td class='text-right'>{anterior.get('pct_despesa', 0):.2f}%</td><td class='text-right'>-</td></tr>")
                    html_parts.append("</tbody></table>")
                    
                    # Gráfico de barras (igual ao BP)
                    labels = ["Receita Realizada", "Despesa Empenhada", "Superávit/Déficit", "Restos a Pagar", "Receita Orçada", "Despesa Orçada"]
                    atual_vals = [
                        atual.get('receita_realizada', 0),
                        atual.get('despesa_empenhada', 0),
                        atual.get('superavit', 0),
                        atual.get('restos_pagar', 0),
                        atual.get('receita_orcada', 0),
                        atual.get('despesa_orcada', 0)
                    ]
                    ant_vals = [
                        anterior.get('receita_realizada', 0),
                        anterior.get('despesa_empenhada', 0),
                        anterior.get('superavit', 0),
                        anterior.get('restos_pagar', 0),
                        anterior.get('receita_orcada', 0),
                        anterior.get('despesa_orcada', 0)
                    ]
                    html_parts.append("<div class='grafico'><canvas id='chartBO'></canvas></div>")
                    html_parts.append("<script>")
                    html_parts.append("new Chart(document.getElementById('chartBO'), {")
                    html_parts.append("type: 'bar',")
                    html_parts.append(f"data: {{ labels: {json.dumps(labels)}, datasets: [")
                    html_parts.append(f"{{ label: 'Atual', data: {json.dumps(atual_vals)}, backgroundColor: '#004b8d' }},")
                    html_parts.append(f"{{ label: 'Anterior', data: {json.dumps(ant_vals)}, backgroundColor: '#6c757d' }}")
                    html_parts.append("] },")
                    html_parts.append("options: { responsive: true, plugins: { legend: { position: 'top' } } }")
                    html_parts.append("});")
                    html_parts.append("</script>")
                
                '''
    
    conteudo = conteudo[:idx_bo] + novo_bloco + conteudo[idx_fim:]
    print("✅ Gráfico de barras adicionado ao Balanço Orçamentário (BO).")
else:
    print("❌ Bloco da Análise Orçamentária não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
