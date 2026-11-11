import re
p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# 1) Remover as 5 linhas com <b>N.</b> que fazem parte do html_declaracao
novas = []
removidas = 0
for l in linhas:
    if '<b>1.</b>' in l or '<b>2.</b>' in l or '<b>3.</b>' in l or '<b>4.</b>' in l or '<b>5.</b>' in l:
        # Verifica se é linha de declaracao (tem <p style e string python)
        if "'<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\">" in l and '</p>' in l:
            removidas += 1
            continue
    novas.append(l)
print(f'Removidas: {removidas} linhas hardcoded')
if removidas != 5:
    print('ERRO: esperava 5')
    raise SystemExit(1)

# 2) Inserir '+ html_itens_declaracao' logo após a linha 'Declaramos ... que:</p>'
inseriu = False
for i, l in enumerate(novas):
    if 'Declaramos' in l and 'que:</p>' in l:
        novas.insert(i + 1, '        + html_itens_declaracao\n')
        inseriu = True
        break
if not inseriu:
    print('ERRO: linha Declaramos nao encontrada')
    raise SystemExit(1)

conteudo = ''.join(novas)
# 3) Garantir que html_itens_declaracao está definido antes de html_declaracao
if 'html_itens_declaracao = ' not in conteudo:
    print('AVISO: definindo html_itens_declaracao...')
    idx = conteudo.find('    html_declaracao = (')
    if idx == -1:
        print('ERRO: html_declaracao nao encontrado')
        raise SystemExit(1)
    leitura = '''    conn2 = sqlite3.connect(db_path)
    cur2 = conn2.cursor()
    cur2.execute(\"SELECT texto FROM itens_declaracao_conformidade WHERE ativo = TRUE ORDER BY ordem, id\")
    itens_decl = [r[0] for r in cur2.fetchall()]
    conn2.close()
    html_itens_declaracao = \"\"
    for i, txt in enumerate(itens_decl, start=1):
        html_itens_declaracao += '<p style=\"text-align: justify; line-height: 1.6; font-size: 13px; margin-bottom: 12px;\"><b>' + str(i) + '.</b> ' + txt + '</p>'

'''
    conteudo = conteudo[:idx] + leitura + conteudo[idx:]

with open(p, 'w', encoding='utf-8') as f:
    f.write(conteudo)
print('OK: 5 paragrafos removidos + html_itens_declaracao referenciado')
