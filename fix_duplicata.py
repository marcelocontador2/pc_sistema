p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Remove as linhas 9784 a 9788 (índices 9783 a 9787) que estão sobrando
del linhas[9783:9788]

with open(p, 'w', encoding='utf-8') as f:
    f.writelines(linhas)
print('OK: Linhas duplicadas removidas. Sintaxe do main.py corrigida.')
