import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_integridade_vermelho")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o trecho da tabela de Integridade
idx_integridade = conteudo.find('if nome_interno == "Integridade entre Demonstrações":')
if idx_integridade != -1:
    # Encontra o final do bloco (próximo elif ou except)
    idx_fim = conteudo.find('elif nome_interno ==', idx_integridade)
    if idx_fim == -1:
        idx_fim = conteudo.find('except Exception', idx_integridade)
    
    novo_bloco = '''if nome_interno == "Integridade entre Demonstrações":
                    matriz = mod_dados.get("matriz", [])
                    html_parts.append("<p style='font-size: 6.2pt; color:#666; font-style:italic;'>Matriz de integridade com o cruzamento de todas as demonstrações.</p>")
                    html_parts.append("<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF.</th></tr></thead><tbody>")
                    for mi in matriz:
                        item = mi.get('item', '')
                        balancete = str(mi.get('balancete', '')).replace('R$', '').strip()
                        bp = str(mi.get('bp', '')).replace('R$', '').strip()
                        bf = str(mi.get('bf', '')).replace('R$', '').strip()
                        bo = str(mi.get('bo', '')).replace('R$', '').strip()
                        dfc = str(mi.get('dfc', '')).replace('R$', '').strip()
                        dvp = str(mi.get('dvp', '')).replace('R$', '').strip()
                        dmpl = str(mi.get('dmpl', '')).replace('R$', '').strip()
                        conf = mi.get('conf', 'OK')
                        
                        # Define a cor com base no status
                        if conf == "OK":
                            cor_conf = "#006400"  # Verde
                        elif conf.startswith("(") or conf.startswith("(("):
                            cor_conf = "#cc0000"  # Vermelho
                        else:
                            cor_conf = "#333333"  # Padrão
                        
                        html_parts.append(f"<tr><td>{item}</td><td class='text-right'>{balancete}</td><td class='text-right'>{bp}</td><td class='text-right'>{bf}</td><td class='text-right'>{bo}</td><td class='text-right'>{dfc}</td><td class='text-right'>{dvp}</td><td class='text-right'>{dmpl}</td><td class='text-center' style='color: {cor_conf}; font-weight: bold;'>{conf}</td></tr>")
                    html_parts.append("</tbody></table>")
                    html_parts.append("<div class='alerta-info'>1. Os itens de conformidade em vermelho, de 1 a 4, são por estornos de restos a pagar.<br>2. Incorporação de Ativos: SOMA = 16.271.957,08.</div>")
                
                '''
    
    conteudo = conteudo[:idx_integridade] + novo_bloco + conteudo[idx_fim:]
    print("✅ Tabela de Integridade ajustada: status (1), (2), etc. em vermelho; OK em verde.")
else:
    print("❌ Bloco da Integridade não encontrado.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
