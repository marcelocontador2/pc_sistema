from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Procurar a linha onde o limite e a margem sao exibidos
# (a tabela tem "Limite Resolução Cofen 814/2026" com "50,00%" fixo)

# Vamos procurar o ID do elemento que mostra a margem e o limite
# e substituir o conteudo fixo por variaveis do JS

trecho_limite = '<tr><td>Limite Resolução Cofen 814/2026</td><td id="comp-limite" class="texto-direita">0,00</td><td class="texto-centro">50,00%</td></tr>'
novo_limite = '<tr><td>Limite Resolução Cofen 814/2026</td><td id="comp-limite" class="texto-direita">0,00</td><td id="comp-limite-pct" class="texto-centro">50,00%</td></tr>'

if trecho_limite in conteudo:
    conteudo = conteudo.replace(trecho_limite, novo_limite)
    print("OK: Linha do limite atualizada com ID comp-limite-pct")
else:
    # Tentar variação (se o texto ja foi alterado antes)
    import re
    padrao = r'<tr><td>Limite[^<]*</td><td id="comp-limite"[^>]*>[^<]*</td><td[^>]*>50,00%</td></tr>'
    if re.search(padrao, conteudo):
        conteudo = re.sub(padrao, novo_limite, conteudo)
        print("OK: Linha do limite atualizada via regex")
    else:
        print("AVISO: nao achei a linha do limite")

# 2. Agora precisamos atualizar o JavaScript que preenche a tabela
# (a funcao que processa o retorno da API)

# Procurar onde o comp-limite é preenchido
# Provavelmente tem algo como: el('comp-limite').innerText = ...
# Vamos procurar por "comp-limite" no JS
import re
padrao_js = r"el\('comp-limite'\)\.innerText\s*=\s*[^;]+;"
match = re.search(padrao_js, conteudo)

if match:
    print(f"Encontrado: {match.group(0)}")
    # Substituir para usar d.limite_atual e d.limite_pct
    novo_js = "el('comp-limite').innerText = fmt(d.limite_atual || 0); el('comp-limite-pct').innerText = fmtPct((d.limite_pct || 0.5) * 100);"
    conteudo = conteudo.replace(match.group(0), novo_js, 1)
    print("OK: JS do limite atualizado")
else:
    print("AVISO: nao achei o JS do comp-limite")

# 3. Atualizar a margem (se existir)
padrao_margem = r"el\('comp-margem'\)\.innerText\s*=\s*[^;]+;"
match_margem = re.search(padrao_margem, conteudo)

if match_margem:
    print(f"Encontrado: {match_margem.group(0)}")
    novo_js_margem = "el('comp-margem').innerText = fmt(d.margem_disponivel_atual || 0);"
    conteudo = conteudo.replace(match_margem.group(0), novo_js_margem, 1)
    print("OK: JS da margem atualizado")
else:
    print("AVISO: nao achei o JS do comp-margem")

arquivo.write_text(conteudo, encoding="utf-8")
print("\nOK: HTML do Custo Pessoal atualizado!")
