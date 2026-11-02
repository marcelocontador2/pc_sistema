c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Adiciona a opção "Centro de Custos" no select, se não existir
if "Centro de Custos" not in c:
    # Procura a linha do select e adiciona a nova opção
    c = c.replace(
        '<option value="DMPL">DMPL</option>',
        '<option value="DMPL">DMPL</option>\n                <option value="Centro de Custos">Centro de Custos</option>'
    )
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Opção 'Centro de Custos' adicionada ao dropdown!")
else:
    print("[AVISO] A opção já existe no dropdown.")
