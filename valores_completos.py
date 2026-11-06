import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\relatorio_comparativo_receitas_v2.html"

shutil.copy2(arquivo, f"{arquivo}.bak_valores_completos_{ts}")
c = open(arquivo, encoding='utf-8').read()

# Localiza o bloco que monta o htmlGrupos e substitui fmtMi por fmt
# Vou usar uma regex que pega o bloco atual
padrao = r"htmlGrupos \+= \s*'<div class=\"grupo-item\".*?</div>';"

if re.search(padrao, c, re.DOTALL):
    novo_bloco = """htmlGrupos += 
        '<div class="grupo-item" style="border-left-color: ' + cor + ';">' +
            '<div class="grupo-nome">' + capitalizeNome(g.nome) + '</div>' +
            '<div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 4px;">' +
                '<div style="font-size: 13px; color: #1e293b;">' +
                    '<strong>Recebido:</strong> R$ ' + fmt(valorAtual) +
                '</div>' +
                '<div style="font-size: 11px; color: #64748b;">' +
                    'Anterior: R$ ' + (anterior > 0 ? fmt(anterior) : '—') +
                '</div>' +
            '</div>' +
            '<div style="font-size: 12px; color: ' + cor + '; font-weight: bold;">' +
                seta + ' R$ ' + fmt(variacao) + ' (' + (anterior > 0 ? fmtPct(pct) : 'Sem dados anteriores') + ')' +
            '</div>' +
        '</div>';"""
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Valores completos aplicados (sem abreviação em mi).")
else:
    print("[AVISO] Bloco não encontrado com regex. Tentando substituições diretas...")
    # Fallback: substitui as chamadas dentro do bloco
    c = c.replace("fmtMi(valorAtual)", "fmt(valorAtual)")
    c = c.replace("fmtMi(anterior)", "fmt(anterior)")
    c = c.replace("fmtMi(variacao)", "fmt(variacao)")
    c = c.replace("txtAtual = fmtMi(valorAtual)", "txtAtual = fmt(valorAtual)")
    c = c.replace("txtAnterior = anterior > 0 ? fmtMi(anterior) : '—'", "txtAnterior = anterior > 0 ? fmt(anterior) : '—'")
    c = c.replace("txtVariacao = fmtMi(variacao)", "txtVariacao = fmt(variacao)")

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Arquivo salvo.")
print("\n=== RESULTADO ESPERADO ===")
print("Recebido: R$ 20.058.909,55")
print("Anterior: R$ 24.169.350,68")
print("▼ R$ -4.110.441,13 (-17,01%)")
