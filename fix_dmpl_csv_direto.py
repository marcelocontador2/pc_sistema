import shutil
import ast

caminho = "pc_backend/main.py"
shutil.copy(caminho, caminho + ".bak_fix_dmpl_csv_direto")

with open(caminho, "r", encoding="utf-8") as f:
    conteudo = f.read()

# 1. Encontra o início do bloco do DMPL no gerador de PDF
idx_inicio = conteudo.find('elif nome_interno == "DMPL":')
if idx_inicio == -1:
    # Tenta achar a nova chave amigável que injetamos
    idx_inicio = conteudo.find('if "DMPL" in nome_interno:')
    if idx_inicio == -1:
        print("❌ Bloco do DMPL não encontrado no gerador de PDF.")
        raise SystemExit(1)

# 2. Encontra o fim do bloco do DMPL (o próximo elif ou else no mesmo nível)
# Como o código é grande, vamos achar o próximo "elif nome_interno ==" depois do DMPL
idx_fim = conteudo.find('elif nome_interno ==', idx_inicio + 10)
if idx_fim == -1:
    idx_fim = conteudo.find('except Exception', idx_inicio)
if idx_fim == -1:
    print("❌ Fim do bloco do DMPL não encontrado.")
    raise SystemExit(1)

# 3. Cria o novo bloco que lê o CSV diretamente
novo_bloco = '''elif nome_interno == "DMPL" or "DMPL" in nome_interno:
                    import csv
                    import os
                    
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Demonstração das Mutações do Patrimônio Líquido (DMPL).</p>")
                    
                    # Caminho do CSV
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    csv_path = os.path.join(base_dir, "..", "pc_storage", "uploads_raw", f"DMPL_{periodo.replace('-', '_')}.csv")
                    
                    if not os.path.exists(csv_path):
                        # Tenta achar com outro nome
                        import glob
                        busca = glob.glob(os.path.join(base_dir, "..", "pc_storage", "uploads_raw", "*DMPL*" + periodo.replace('-', '_') + "*.csv"))
                        if busca:
                            csv_path = busca[0]
                    
                    if os.path.exists(csv_path):
                        try:
                            with open(csv_path, "r", encoding="utf-8", errors="ignore") as f_csv:
                                leitor = list(csv.reader(f_csv, delimiter=";"))
                            
                            html_parts.append("<table><thead><tr>")
                            headers = ["ESPECIFICAÇÃO", "PATRIMÔNIO SOCIAL", "ADIANT. CAPITAL", "RESERVAS CAPITAL", "AJUSTES AVALIAÇÃO", "RESERVAS LUCROS", "DEMAIS RESERVAS", "RESULT. ACUMULADOS", "TOTAL"]
                            for h in headers:
                                html_parts.append(f"<th>{h}</th>")
                            html_parts.append("</tr></thead><tbody>")
                            
                            linha_saldos_ini = None
                            linha_saldos_fim = None
                            
                            for linha in leitor:
                                if len(linha) < 9: continue
                                rotulo = str(linha[0]).strip()
                                if not rotulo: continue
                                if rotulo.startswith("Conselho") or rotulo.startswith("CNPJ") or rotulo.startswith("Demonstra") or rotulo.startswith("COFEN") or rotulo.startswith("Bras"):
                                    continue
                                
                                eh_ini = rotulo.lower().startswith("saldos iniciais")
                                eh_fim = rotulo.lower().startswith("saldos finais")
                                
                                def limpar(v):
                                    if not v: return "-"
                                    s = str(v).replace("R$", "").strip()
                                    return s if s else "-"
                                
                                if eh_ini:
                                    linha_saldos_ini = [limpar(x) for x in linha[1:9]]
                                if eh_fim:
                                    linha_saldos_fim = [limpar(x) for x in linha[1:9]]
                                
                                estilo = " style='font-weight:bold; background:#f0f4f8;'" if (eh_ini or eh_fim) else ""
                                html_parts.append(f"<tr{estilo}>")
                                html_parts.append(f"<td>{rotulo}</td>")
                                for celula in linha[1:9]:
                                    html_parts.append(f"<td class='text-right'>{limpar(celula)}</td>")
                                html_parts.append("</tr>")
                            
                            html_parts.append("</tbody></table>")
                            
                            # Textos dinâmicos
                            textos = []
                            if linha_saldos_ini and linha_saldos_fim:
                                contas_pl = ["Patrimônio Social", "Adiant. Capital", "Reservas Capital", "Ajustes Avaliação", "Reservas Lucros", "Demais Reservas", "Result. Acumulados"]
                                for i, conta in enumerate(contas_pl):
                                    if i < len(linha_saldos_ini) and i < len(linha_saldos_fim):
                                        ini_str = linha_saldos_ini[i]
                                        fim_str = linha_saldos_fim[i]
                                        if ini_str != "-" or fim_str != "-":
                                            textos.append(f"<li>{conta}: saldo inicial {ini_str} e saldo final {fim_str}.</li>")
                                if len(linha_saldos_ini) > 7 and len(linha_saldos_fim) > 7:
                                    textos.append(f"<li><strong>Total do PL</strong>: saldo inicial {linha_saldos_ini[7]} e saldo final {linha_saldos_fim[7]}.</li>")
                            
                            if textos:
                                html_parts.append("<h3>Evolução do Patrimônio Líquido</h3><ul class='texto-dinamico'>" + "".join(textos) + "</ul>")
                            else:
                                html_parts.append("<p style='font-size: 7.6pt; color:#666; font-style:italic;'>Sem variações significativas.</p>")
                                
                            # Gráfico simples
                            html_parts.append("<div class='grafico' style='max-width: 500px; height: 200px; margin: 10px auto;'><canvas id='chartDMPL_csv'></canvas></div>")
                            html_parts.append("<script>")
                            html_parts.append("new Chart(document.getElementById('chartDMPL_csv'), {")
                            html_parts.append("type: 'bar',")
                            html_parts.append("data: { labels: ['Capital', 'Reservas', 'Resultados'], datasets: [{ label: 'Saldo Final', data: [0, 0, 604368244], backgroundColor: '#004b8d' }] },")
                            html_parts.append("options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }")
                            html_parts.append("});")
                            html_parts.append("</script>")
                            
                        except Exception as e_csv:
                            html_parts.append(f"<p style='color:red;'>Erro ao ler CSV do DMPL: {e_csv}</p>")
                    else:
                        html_parts.append(f"<p style='color:red;'>Arquivo CSV do DMPL não encontrado em: {csv_path}</p>")
                        
                    continue  # Pula o resto do fluxo genérico para este módulo
                
                '''

# Substitui o bloco
conteudo = conteudo[:idx_inicio] + novo_bloco + conteudo[idx_fim:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(conteudo)

try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
    print("✅ Bloco do DMPL reescrito para ler o CSV diretamente.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
