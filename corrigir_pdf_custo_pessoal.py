from pathlib import Path

# ============ 1. ATUALIZAR O HTML DO PDF COMPLETO ============
arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# Trocar LRF por Resolucao Cofen 814/2026
conteudo = conteudo.replace("Custo de Pessoal x Limite da LRF (Art. 19)", "Custo de Pessoal x Limite da Resolução Cofen 814/2026")
conteudo = conteudo.replace("Limite LRF (50% da RCL)", "Limite Resolução Cofen 814/2026")
conteudo = conteudo.replace("Limite LRF", "Limite Resolução Cofen 814/2026")
conteudo = conteudo.replace("Margem Disponível (Limite LRF - Custo)", "Margem Disponível (Limite Resolução Cofen 814/2026 - Custo)")
conteudo = conteudo.replace("Teto estabelecido pelo Art. 19 da LRF", "Teto estabelecido pela Resolução Cofen 814/2026")

# Adicionar leitura do entidade da URL
# (o HTML provavelmente tem um script que le o periodo da URL, precisamos adicionar o entidade)
if "entidade" not in conteudo:
    # Procurar o script que le o periodo
    trecho_periodo = "const periodo = new URLSearchParams(window.location.search).get('periodo')"
    if trecho_periodo in conteudo:
        conteudo = conteudo.replace(
            trecho_periodo,
            trecho_periodo + ";\n        const entidade = new URLSearchParams(window.location.search).get('entidade') || 'COFEN'"
        )
        print("OK: PDF completo - entidade adicionada a URL")
    else:
        print("AVISO: PDF completo - nao achei o trecho do periodo")
else:
    print("OK: PDF completo - entidade ja existe")

# Atualizar o fetch para enviar entidade
if "?entidade=" not in conteudo:
    conteudo = conteudo.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: PDF completo - fetch atualizado")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: PDF completo atualizado!")

# ============ 2. ATUALIZAR O HTML DO PDF RESUMO ============
arquivo2 = Path("pc_frontend/custo_pessoal_pdf_resumo.html")
conteudo2 = arquivo2.read_text(encoding="utf-8")

# Trocar LRF por Resolucao Cofen 814/2026
conteudo2 = conteudo2.replace("Custo de Pessoal x Limite da LRF", "Custo de Pessoal x Limite da Resolução Cofen 814/2026")
conteudo2 = conteudo2.replace("Limite LRF", "Limite Resolução Cofen 814/2026")
conteudo2 = conteudo2.replace("Margem Disponível (Limite LRF - Custo)", "Margem Disponível (Limite Resolução Cofen 814/2026 - Custo)")

# Adicionar entidade
if "entidade" not in conteudo2:
    trecho_periodo2 = "const periodo = new URLSearchParams(window.location.search).get('periodo')"
    if trecho_periodo2 in conteudo2:
        conteudo2 = conteudo2.replace(
            trecho_periodo2,
            trecho_periodo2 + ";\n        const entidade = new URLSearchParams(window.location.search).get('entidade') || 'COFEN'"
        )
        print("OK: PDF resumo - entidade adicionada a URL")

# Atualizar fetch
if "?entidade=" not in conteudo2:
    conteudo2 = conteudo2.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: PDF resumo - fetch atualizado")

arquivo2.write_text(conteudo2, encoding="utf-8")
print("OK: PDF resumo atualizado!")
