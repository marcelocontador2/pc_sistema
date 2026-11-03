import shutil, datetime

arquivo = 'analise_comparativo_receitas.html'
shutil.copy2(arquivo, f"{arquivo}.bak_cards_{datetime.datetime.now().strftime('%H%M%S')}")
c = open(arquivo, encoding='utf-8').read()

# 1. Inverter a ordem dos cards no HTML
card_realizada = """            <div class="card receita">
                <div class="card-title">Receita Realizada</div>
                <div class="card-value" id="resumo-realizado">R$ 0,00</div>
                <div class="card-sub" id="resumo-realizado-anterior">Anterior: R$ 0,00</div>
            </div>"""

card_orcada = """            <div class="card receita">
                <div class="card-title">Receita Orçada</div>
                <div class="card-value" id="resumo-orcado">R$ 0,00</div>
                <div class="card-sub" id="resumo-orcado-anterior">Anterior: R$ 0,00</div>
            </div>"""

if card_realizada in c and card_orcada in c:
    # Substitui temporariamente para não sobrescrever
    c = c.replace(card_realizada, "<!--TEMP_REALIZADA-->")
    c = c.replace(card_orcada, card_realizada)
    c = c.replace("<!--TEMP_REALIZADA-->", card_orcada)
    print("[OK] Ordem dos cards invertida!")
else:
    print("[AVISO] Cards não encontrados no formato exato.")

# 2. Atualizar os cabeçalhos da tabela no JavaScript
c = c.replace("<th class=\"text-right\">Período Atual (R$)</th>", "<th class=\"text-right\">Realizada (Per. Atual) R$</th>")
c = c.replace("<th class=\"text-right\">Período Anterior (R$)</th>", "<th class=\"text-right\">Realizada (Per. Anterior) R$</th>")

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Cabeçalhos da tabela atualizados para 'Receita Realizada'!")
