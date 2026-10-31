from pathlib import Path

# Corrigir PDF completo
arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Adicionar a linha do entidade logo apos o periodo
trecho_antigo = "const periodo = urlParams.get('periodo') || '2026-TRIMESTRE-3';"
trecho_novo = """const periodo = urlParams.get('periodo') || '2026-TRIMESTRE-3';
            const entidade = urlParams.get('entidade') || 'COFEN';"""

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo, 1)
    print("OK: entidade adicionada no PDF completo!")
else:
    print("AVISO: nao achei o periodo no PDF completo")

# Se ainda nao tem o fetch atualizado, atualizar
if "?entidade=" not in conteudo:
    conteudo = conteudo.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: fetch do PDF completo atualizado")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: PDF completo corrigido!")

# Corrigir PDF resumo
arquivo2 = Path("pc_frontend/custo_pessoal_pdf_resumo.html")
conteudo2 = arquivo2.read_text(encoding="utf-8")

# Verificar se tem o mesmo problema
if "entidade" not in conteudo2:
    # Procurar o periodo
    import re
    padrao = r"(const periodo = [^;]+;)"
    match = re.search(padrao, conteudo2)
    if match:
        conteudo2 = conteudo2.replace(
            match.group(1),
            match.group(1) + "\n        const entidade = new URLSearchParams(window.location.search).get('entidade') || 'COFEN';",
            1
        )
        print("OK: entidade adicionada no PDF resumo!")
    else:
        print("AVISO: nao achei o periodo no PDF resumo")

# Se o fetch ainda nao tem entidade, atualizar
if "?entidade=" not in conteudo2:
    conteudo2 = conteudo2.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: fetch do PDF resumo atualizado")

arquivo2.write_text(conteudo2, encoding="utf-8")
print("OK: PDF resumo corrigido!")
