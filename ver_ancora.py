p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()
for i, l in enumerate(linhas):
    if 'Declaramos' in l:
        print(f'LINHA {i+1}:')
        print(repr(l))
        print()
        print('--- 3 linhas seguintes ---')
        for j in range(i+1, min(i+4, len(linhas))):
            print(f'{j+1}: {repr(linhas[j])}')
        break
