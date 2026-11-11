p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Mostra as linhas ao redor do erro para confirmarmos
print("=== Linhas 9805 a 9825 ===")
for i in range(9804, min(9825, len(linhas))):
    print(f"{i+1}: {linhas[i].rstrip()}")

# Remove o bloco duplicado de except/finally (linhas 9816 a 9820)
# Vamos procurar o padrao exato e deletar
if "except Exception as e:" in linhas[9815] and "conn.rollback()" in linhas[9816]:
    del linhas[9815:9820]
    with open(p, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("\nOK: Linhas duplicadas removidas.")
else:
    print("\nAVISO: O padrao nao bateu. Nao removi nada.")
