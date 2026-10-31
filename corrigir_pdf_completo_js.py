from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal_pdf_completo.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Substituir o calculo do limite e da margem
trecho_antigo = '''                    const rcl = d.rcl_total;
                    const custo = d.custo_total;
                    const limite = rcl * 0.5;
                    const margem = limite - custo;'''

trecho_novo = '''                    const rcl = d.rcl_atual || d.rcl_total || 0;
                    const custo = d.custo_atual || d.custo_total || 0;
                    const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));
                    const margem = d.margem_disponivel_atual || (limite - custo);
                    const limite_pct = d.limite_pct || 0.5;'''

if trecho_antigo in conteudo:
    conteudo = conteudo.replace(trecho_antigo, trecho_novo)
    print("OK: Calculo do limite e margem atualizado!")
else:
    print("AVISO: nao achei o trecho exato. Tentando regex...")
    import re
    padrao = r"const rcl = d\.rcl_total;\s*const custo = d\.custo_total;\s*const limite = rcl \* 0\.5;\s*const margem = limite - custo;"
    if re.search(padrao, conteudo):
        conteudo = re.sub(
            padrao,
            "const rcl = d.rcl_atual || d.rcl_total || 0;\n                    const custo = d.custo_atual || d.custo_total || 0;\n                    const limite = d.limite_atual || (rcl * (d.limite_pct || 0.5));\n                    const margem = d.margem_disponivel_atual || (limite - custo);\n                    const limite_pct = d.limite_pct || 0.5;",
            conteudo
        )
        print("OK: Calculo atualizado via regex!")
    else:
        print("ERRO: nao achei o calculo")

# 2. Atualizar os campos de exibicao para usar os novos valores
conteudo = conteudo.replace(
    "document.getElementById('pdf-limite').innerText = fmt(limite);",
    "document.getElementById('pdf-limite').innerText = fmt(limite) + ' (' + (limite_pct * 100).toFixed(2) + '%)';"
)

# 3. Corrigir os valores de RCL (usar rcl_atual e rcl_anterior)
conteudo = conteudo.replace(
    "const rclAtual = d.rcl_atual || (rcl * 0.8);",
    "const rclAtual = d.rcl_atual || 0;"
)
conteudo = conteudo.replace(
    "const rclAnterior = d.rcl_anterior || (rcl * 0.2);",
    "const rclAnterior = d.rcl_anterior || 0;"
)

# 4. Corrigir os textos do PDF (ja foram trocados, mas garantir)
conteudo = conteudo.replace("Limite LRF (50% da RCL)", "Limite Resolução Cofen 814/2026")
conteudo = conteudo.replace("Limite LRF", "Limite Resolução Cofen 814/2026")

# 5. Atualizar o texto do limite para mostrar o percentual dinamicamente
# (procurar o trecho que mostra 50,00% fixo)
conteudo = conteudo.replace(
    "Limite Resolução Cofen 814/2026 (50% da RCL)",
    "Limite Resolução Cofen 814/2026 (<span id='pdf-limite-pct-text'>50,00%</span> da RCL)"
)

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: PDF completo corrigido!")
