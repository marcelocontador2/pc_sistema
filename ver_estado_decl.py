p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
for i, l in enumerate(linhas):
    if 'html_itens_declaracao =' in l or 'html_declaracao = (' in l:
        print(f'--- LINHA {i+1} ---')
        print(repr(l))
        print('--- CONTEXTO (5 antes + 5 depois) ---')
        for j in range(max(0, i-5), min(len(linhas), i+15)):
            marcador = '>>>' if j == i else '   '
            print(f'{marcador} {j+1}: {linhas[j].rstrip()[:120]}')
        print()
