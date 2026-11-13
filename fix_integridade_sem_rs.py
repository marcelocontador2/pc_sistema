import shutil
import ast

caminho_main = "pc_backend/main.py"
shutil.copy(caminho_main, caminho_main + ".bak_fix_integridade_sem_rs")

with open(caminho_main, "r", encoding="utf-8") as f:
    conteudo = f.read()

# Localiza o trecho da tabela de Integridade
trecho_antigo = '''                    html_parts.append("<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF.</th></tr></thead><tbody>")
                    for mi in matriz:
                        html_parts.append(f"<tr><td>{mi.get('item','')}</td><td class='text-right'>{mi.get('balancete','')}</td><td class='text-right'>{mi.get('bp','')}</td><td class='text-right'>{mi.get('bf','')}</td><td class='text-right'>{mi.get('bo','')}</td><td class='text-right'>{mi.get('dfc','')}</td><td class='text-right'>{mi.get('dvp','')}</td><td class='text-right'>{mi.get('dmpl','')}</td><td class='text-center'>{mi.get('conf','')}</td></tr>")
                    html_parts.append("</tbody></table>")'''

trecho_novo = '''                    html_parts.append("<table><thead><tr><th>ITEM</th><th>BALANCETE</th><th>BP</th><th>BF</th><th>BO</th><th>DFC</th><th>DVP</th><th>DMPL</th><th>CONF.</th></tr></thead><tbody>")
                    for mi in matriz:
                        # Remove o "R$" dos valores, mantendo apenas os números formatados
                        balancete = str(mi.get('balancete', '')).replace('R$', '').strip()
                        bp = str(mi.get('bp', '')).replace('R$', '').strip()
                        bf = str(mi.get('bf', '')).replace('R$', '').strip()
                        bo = str(mi.get('bo', '')).replace('R$', '').strip()
                        dfc = str(mi.get('dfc', '')).replace('R$', '').strip()
                        dvp = str(mi.get('dvp', '')).replace('R$', '').strip()
                        dmpl = str(mi.get('dmpl', '')).replace('R$', '').strip()
                        conf = mi.get('conf', '')
                        html_parts.append(f"<tr><td>{mi.get('item','')}</td><td class='text-right'>{balancete}</td><td class='text-right'>{bp}</td><td class='text-right'>{bf}</td><td class='text-right'>{bo}</td><td class='text-right'>{dfc}</td><td class='text-right'>{dvp}</td><td class='text-right'>{dmpl}</td><td class='text-center'>{conf}</td></tr>")
                    html_parts.append("</tbody></table>")'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("✅ Tabela de Integridade ajustada: 'R$' removido dos valores.")
else:
    print("⚠️ Trecho exato não encontrado. Tentando abordagem alternativa...")
    # Tenta substituir apenas as linhas que renderizam os valores
    linhas = conteudo.split("\n")
    novas_linhas = []
    for linha in linhas:
        if "mi.get('balancete','')" in linha or "mi.get('bp','')" in linha:
            # Substitui a renderização para remover R$
            linha = linha.replace("mi.get('balancete','')", "str(mi.get('balancete','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('bp','')", "str(mi.get('bp','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('bf','')", "str(mi.get('bf','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('bo','')", "str(mi.get('bo','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('dfc','')", "str(mi.get('dfc','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('dvp','')", "str(mi.get('dvp','')).replace('R$', '').strip()")
            linha = linha.replace("mi.get('dmpl','')", "str(mi.get('dmpl','')).replace('R$', '').strip()")
        novas_linhas.append(linha)
    conteudo = "\n".join(novas_linhas)
    print("✅ Ajuste aplicado via abordagem alternativa.")

with open(caminho_main, "w", encoding="utf-8") as f:
    f.write(conteudo)

# Verifica sintaxe
try:
    ast.parse(conteudo)
    print("✅ main.py salvo com sintaxe verificada.")
except SyntaxError as e:
    print(f"❌ Erro de sintaxe na linha {e.lineno}: {e.text}")
