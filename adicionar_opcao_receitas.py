c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona a opção no dropdown de tipo de relatório
if "COMPARATIVO_RECEITAS" not in c:
    c = c.replace(
        '<option value="CENTRO_CUSTOS">Centro de Custos</option>',
        '<option value="CENTRO_CUSTOS">Centro de Custos</option>\n            <option value="COMPARATIVO_RECEITAS">Comparativo de Receitas</option>'
    )
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Opção 'Comparativo de Receitas' adicionada ao dropdown!")
else:
    print("[AVISO] Opção já existe.")
