from pathlib import Path
import re

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Remover o select antigo de entidade (aquele com "COFEN (Limite 50%)")
# Procurar por <select id="entidade-select" ...> ... </select>
padrao_select = r'<select\s+id="entidade-select"[^>]*>.*?</select>'
match = re.search(padrao_select, conteudo, re.DOTALL)

if match:
    print(f"Encontrado select antigo: {match.group(0)[:100]}...")
    conteudo = conteudo.replace(match.group(0), "")
    print("OK: Select antigo removido!")
else:
    print("AVISO: nao achei o select antigo de entidade")

# Verificar se ainda tem o fetch antigo que usava entidade-select
if "entidade-select" in conteudo:
    # Procurar a linha que usa el('entidade-select')
    padrao_js = r"var\s+entidade\s*=\s*encodeURIComponent\(el\('entidade-select'\)\.value\);\s*"
    match_js = re.search(padrao_js, conteudo)
    if match_js:
        conteudo = conteudo.replace(match_js.group(0), "")
        print("OK: Codigo JS que usava entidade-select removido!")
    
    # Verificar se ainda tem referencias
    if "entidade-select" in conteudo:
        print("AVISO: ainda ha referencias a entidade-select no HTML")
    else:
        print("OK: Nenhuma referencia a entidade-select restante!")

# Tambem remover o fetch antigo que passava ?entidade=
padrao_fetch = r"fetch\('/api/custo_pessoal/'\s*\+\s*periodo\s*\+\s*'\?entidade='\s*\+\s*entidade\)"
match_fetch = re.search(padrao_fetch, conteudo)
if match_fetch:
    conteudo = conteudo.replace(match_fetch.group(0), "fetch('/api/custo_pessoal/' + periodo)")
    print("OK: Fetch simplificado (sem ?entidade=)!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: HTML limpo!")
