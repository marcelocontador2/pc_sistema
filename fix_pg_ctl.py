p = 'ligar.ps1'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

for i, l in enumerate(linhas):
    if 'pg_ctl.exe' in l:
        # Substitui a linha inteira pela string perfeita
        linhas[i] = r'        & "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\18\data" -l "C:\temp\pg_auto.log" start' + '\n'

with open(p, 'w', encoding='utf-8') as f:
    f.writelines(linhas)
print('OK: Caminho do pg_ctl corrigido com sucesso no ligar.ps1')
