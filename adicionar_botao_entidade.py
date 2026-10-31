from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar o select de Cofen/Coren ao lado do periodo
trecho_antigo = '<select id="periodo-select"><option value="2026-TRIMESTRE-3">2026 - 3º Trimestre</option></select>'
trecho_novo = '''<select id="periodo-select"><option value="2026-TRIMESTRE-3">2026 - 3º Trimestre</option></select>
            <select id="entidade-select" style="margin-left: 10px;">
                <option value="COFEN">COFEN (Limite 50%)</option>
                <option value="COREN">COREN (Limite 60%)</option>
            </select>'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: Select de Cofen/Coren adicionado!")
else:
    print("AVISO: nao achei o select do periodo")

# 2. Atualizar o fetch para enviar o entidade
trecho_antigo2 = "fetch('/api/custo_pessoal/' + periodo).then(lerJSON).then(function (d) {"
trecho_novo2 = "var entidade = encodeURIComponent(el('entidade-select').value);\n            fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade).then(lerJSON).then(function (d) {"

if trecho_antigo2 in conteudo:
    conteudo = conteudo.replace(trecho_antigo2, trecho_novo2, 1)
    print("OK: Fetch atualizado para enviar o entidade!")
else:
    print("AVISO: nao achei o fetch do custo pessoal")

# 3. Atualizar os labels "LRF" para "Resolução Cofen 814/2026"
conteudo = conteudo.replace("Limite LRF", "Limite Resolução Cofen 814/2026")
conteudo = conteudo.replace("Limite da LRF", "Limite da Resolução Cofen 814/2026")
conteudo = conteudo.replace("(LRF)", "(Resolução Cofen 814/2026)")
conteudo = conteudo.replace("Custo de Pessoal x Limite da LRF", "Custo de Pessoal x Limite da Resolução Cofen 814/2026")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: Labels LRF substituidos!")
