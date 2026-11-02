c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# O texto exato do dropdown (com a tag option do DMPL)
trecho_antigo = '<option value="DMPL">DMPL</option>'

# Verifica se a opção de Centro de Custos já está LOGO APÓS o DMPL (para não confundir com o menu do final)
if '<option value="CENTRO_CUSTOS">Centro de Custos</option>' not in c:
    if trecho_antigo in c:
        trecho_novo = '<option value="DMPL">DMPL</option>\n            <option value="CENTRO_CUSTOS">Centro de Custos</option>'
        c = c.replace(trecho_antigo, trecho_novo)
        open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
        print("[OK] Opção 'Centro de Custos' adicionada ao dropdown de importação!")
    else:
        print("[ERRO] Não foi possível encontrar o DMPL no arquivo.")
else:
    print("[AVISO] A opção 'CENTRO_CUSTOS' já está no dropdown.")
