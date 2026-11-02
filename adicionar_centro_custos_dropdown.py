c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Verifica se a opção já existe
if "Centro de Custos" not in c:
    # Adiciona a opção logo após o DMPL, com a linha exata
    trecho_antigo = '<option value="DMPL">DMPL</option>'
    trecho_novo = '<option value="DMPL">DMPL</option>\n            <option value="CENTRO_CUSTOS">Centro de Custos</option>'
    
    if trecho_antigo in c:
        c = c.replace(trecho_antigo, trecho_novo)
        open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
        print("[OK] Opção 'Centro de Custos' adicionada com sucesso!")
    else:
        print("[ERRO] Não foi possível encontrar o DMPL no arquivo.")
else:
    print("[AVISO] A opção já existe no arquivo.")
