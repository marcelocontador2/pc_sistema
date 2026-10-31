from pathlib import Path
import re

# ============ PDF COMPLETO ============
arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Garantir que o entidade e lido da URL
if "const entidade = urlParams.get('entidade')" not in conteudo:
    conteudo = conteudo.replace(
        "const periodo = urlParams.get('periodo') || '2026-TRIMESTRE-3';",
        "const periodo = urlParams.get('periodo') || '2026-TRIMESTRE-3';\n            const entidade = urlParams.get('entidade') || 'COREN';"
    )
    print("OK: entidade adicionada no PDF completo!")

# 2. Garantir que o fetch passa o entidade
if "?entidade=" not in conteudo:
    conteudo = conteudo.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: fetch com entidade no PDF completo!")

# 3. Garantir que o limite usa d.limite_atual
if "const limite = rcl * 0.5;" in conteudo:
    conteudo = conteudo.replace(
        "const limite = rcl * 0.5;",
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));"
    )
    print("OK: limite usa d.limite_atual no PDF completo!")

# 4. Adicionar limite_pct no JS (se nao tiver)
if "const limite_pct = d.limite_pct" not in conteudo:
    conteudo = conteudo.replace(
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));",
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));\n                    const limite_pct = d.limite_pct || 0.5;"
    )
    print("OK: limite_pct adicionado no PDF completo!")

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: PDF completo atualizado!")

# ============ PDF RESUMO ============
arquivo2 = Path("pc_frontend/custo_pessoal_pdf_resumo.html")
conteudo2 = arquivo2.read_text(encoding="utf-8")

# 1. Garantir que o entidade e lido da URL
if "const entidade = urlParams.get('entidade')" not in conteudo2:
    match = re.search(r"const periodo = [^;]+;", conteudo2)
    if match:
        conteudo2 = conteudo2.replace(
            match.group(0),
            match.group(0) + "\n            const entidade = urlParams.get('entidade') || 'COREN';"
        )
        print("OK: entidade adicionada no PDF resumo!")

# 2. Garantir que o fetch passa o entidade
if "?entidade=" not in conteudo2:
    conteudo2 = conteudo2.replace(
        "fetch('/api/custo_pessoal/' + periodo)",
        "fetch('/api/custo_pessoal/' + periodo + '?entidade=' + entidade)"
    )
    print("OK: fetch com entidade no PDF resumo!")

# 3. Garantir que o limite usa d.limite_atual
if "const limite = rcl * 0.5;" in conteudo2:
    conteudo2 = conteudo2.replace(
        "const limite = rcl * 0.5;",
        "const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));"
    )
    print("OK: limite usa d.limite_atual no PDF resumo!")

arquivo2.write_text(conteudo2, encoding="utf-8")
print("OK: PDF resumo atualizado!")
