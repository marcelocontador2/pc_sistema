import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_dmpl_consolidado_v1")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o bloco do DMPL (linha 10174) e o fim (próximo elif)
idx_dmpl = conteudo.find('elif nome_interno == "DMPL":')
if idx_dmpl == -1:
    print("❌ Bloco DMPL não encontrado.")
    raise SystemExit(1)

idx_fim_dmpl = conteudo.find('elif nome_interno == "Comparativo de Receitas":', idx_dmpl)
if idx_fim_dmpl == -1:
    print("❌ Fim do bloco DMPL não encontrado.")
    raise SystemExit(1)

novo_bloco = '''elif nome_interno == "DMPL":
                    def fmt_sem_rs(v):
                        if v is None: return "-"
                        if isinstance(v, (int, float)):
                            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        s = str(v).replace("R$", "").strip()
                        if s in ("", "-"): return s
                        # tenta converter BR para float
                        try:
                            n = float(s.replace(".", "").replace(",", "."))
                            return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        except Exception:
                            return s
                    
                    def parse_num(v):
                        if v is None: return 0.0
                        if isinstance(v, (int, float)): return float(v)
                        s = str(v).replace("R$", "").strip()
                        if s in ("", "-"): return 0.0
                        try:
                            return float(s.replace(".", "").replace(",", "."))
                        except Exception:
                            return 0.0
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração das Mutações do Patrimônio Líquido (DMPL).</p>")
                    dados_dmpl = mod_dados.get("dados", [])
                    
                    if not dados_dmpl:
                        html_parts.append("<p style='color:red;'>Dados do DMPL não disponíveis.</p>")
                    else:
                        # Mapeamento das colunas do PL
                        contas_pl = [
                            "Patrimônio Social e Capital Social",
                            "Adiantamento para Futuro Aumento de Capital",
                            "Reservas de Capital",
                            "Ajustes de Avaliação Patrimonial",
                            "Reservas de Lucros",
                            "Demais Reservas",
                            "Resultados Acumulados"
                        ]
                        idx_total = 8
                        
                        # Cabeçalho da tabela (corrigido encoding)
                        headers = ["ESPECIFICAÇÃO"] + contas_pl + ["TOTAL"]
                        html_parts.append("<table><thead><tr>")
                        for h in headers:
                            html_parts.append(f"<th>{h}</th>")
                        html_parts.append("</tr></thead><tbody>")
                        
                        # Linhas de dados (a partir do item 7 = 'Saldos iniciais')
                        linha_saldos_ini = None
                        linha_saldos_fim = None
                        linhas_render = []
                        
                        for linha in dados_dmpl:
                            if not isinstance(linha, list) or len(linha) < 9:
                                continue
                            rotulo = str(linha[0]).strip()
                            # Pula cabeçalho/rodapé
                            if not rotulo: 
                                continue
                            if rotulo.startswith("Conselho Federal") or rotulo.startswith("CNPJ") or rotulo.startswith("Demonstra") or rotulo.startswith("COFEN/BR") or rotulo.startswith("Bras"):
                                continue
                            # É linha de dados
                            eh_saldo_ini = rotulo.lower().startswith("saldos iniciais")
                            eh_saldo_fim = rotulo.lower().startswith("saldos finais")
                            
                            if eh_saldo_ini:
                                linha_saldos_ini = [parse_num(x) for x in linha[1:9]]
                            if eh_saldo_fim:
                                linha_saldos_fim = [parse_num(x) for x in linha[1:9]]
                            
                            linhas_render.append((rotulo, linha, eh_saldo_ini, eh_saldo_fim))
                        
                        # Renderiza linhas
                        for rotulo, linha, eh_ini, eh_fim in linhas_render:
                            estilo = ""
                            if eh_ini or eh_fim:
                                estilo = " style='font-weight:bold; background:#f0f4f8;'"
                            html_parts.append(f"<tr{estilo}>")
                            html_parts.append(f"<td>{rotulo}</td>")
                            for celula in linha[1:9]:
                                html_parts.append(f"<td class='text-right'>{fmt_sem_rs(celula)}</td>")
                            html_parts.append("</tr>")
                        
                        html_parts.append("</tbody></table>")
                        
                        # Textos dinâmicos de evolução
                        textos = []
                        if linha_saldos_ini and linha_saldos_fim:
                            for i, conta in enumerate(contas_pl):
                                ini = linha_saldos_ini[i]
                                fim = linha_saldos_fim[i]
                                if abs(ini) < 0.01 and abs(fim) < 0.01:
                                    continue
                                var_pct = ((fim - ini) / abs(ini) * 100) if abs(ini) > 0.01 else 0
                                direcao = "aumento" if fim > ini else ("redução" if fim < ini else "estabilidade")
                                if abs(ini) <= 0.01:
                                    textos.append(f"<li>{conta}: saldo inicial zerado, passando a {fmt_sem_rs(fim)} no período.</li>")
                                else:
                                    textos.append(f"<li>{conta}: {direcao} de {fmt_sem_rs(ini)} para {fmt_sem_rs(fim)} (variação de {var_pct:+.2f}%).</li>")
                            # Total do PL
                            ini_t = linha_saldos_ini[7]
                            fim_t = linha_saldos_fim[7]
                            if abs(ini_t) > 0.01 or abs(fim_t) > 0.01:
                                var_t = ((fim_t - ini_t) / abs(ini_t) * 100) if abs(ini_t) > 0.01 else 0
                                direcao_t = "aumento" if fim_t > ini_t else ("redução" if fim_t < ini_t else "estabilidade")
                                textos.append(f"<li><strong>Total do Patrimônio Líquido</strong>: {direcao_t} de {fmt_sem_rs(ini_t)} para {fmt_sem_rs(fim_t)} (variação de {var_t:+.2f}%).</li>")
                        
                        if textos:
                            html_parts.append("<h3>Evolução do Patrimônio Líquido</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                        else:
                            html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas entre os períodos.</p>")
                        
                        # Gráfico de barras (Saldo Inicial x Saldo Final por conta do PL)
                        if linha_saldos_ini and linha_saldos_fim:
                            labels = contas_pl
                            ini_vals = linha_saldos_ini[:7]
                            fim_vals = linha_saldos_fim[:7]
                            html_parts.append("<div class='grafico' style='max-width: 500px; height: 220px; margin: 10px auto;'><canvas id='chartDMPL' style='width: 100%; height: 100%;'></canvas></div>")
                            html_parts.append("<script>")
                            html_parts.append("new Chart(document.getElementById('chartDMPL'), {")
                            html_parts.append("type: 'bar',")
                            html_parts.append(f"data: {{ labels: {json.dumps(labels, ensure_ascii=False)}, datasets: [")
                            html_parts.append(f"{{ label: 'Saldo Inicial', data: {json.dumps(ini_vals)}, backgroundColor: '#6c757d' }},")
                            html_parts.append(f"{{ label: 'Saldo Final', data: {json.dumps(fim_vals)}, backgroundColor: '#004b8d' }}")
                            html_parts.append("] },")
                            html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { x: { ticks: { font: { size: 7 } } }, y: { ticks: { font: { size: 7 } } } } }")
                            html_parts.append("});")
                            html_parts.append("</script>")
                
                '''

conteudo = conteudo[:idx_dmpl] + novo_bloco + conteudo[idx_fim_dmpl:]
print("✅ Bloco DMPL substituído (tabela formatada, sem R$, textos dinâmicos e gráfico).")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
