import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
back_path = r"pc_backend\main.py"
shutil.copy2(back_path, f"{back_path}.bak_buscar_def7_{ts}")

c = open(back_path, encoding="utf-8-sig").read()

# Localiza a Definicao 7 (posicao ~153299)
idx = c.find('def buscar(termo, coluna):', 150000)
if idx == -1:
    print("[ERRO] Definicao 7 nao encontrada.")
    exit(1)

# Pega o bloco (ate o proximo "def" ou 500 chars)
fim = c.find('\ndef ', idx + 10)
if fim == -1:
    fim = idx + 500
bloco = c[idx:fim]

print("=" * 70)
print("DEFINICAO 7 ATUAL")
print("=" * 70)
print(bloco)

# Substitui pela versao corrigida
bloco_novo = '''def buscar(termo, coluna):
            termo_upper = termo.upper()
            for p in l_bp:
                # Procura o termo na coluna 0 (Ativo) ou 3 (Passivo)
                for col_espec in [0, 3]:
                    if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                        # Pega o valor da coluna seguinte (1 para Ativo, 4 para Passivo)
                        col_valor = col_espec + 1
                        if len(p) > col_valor:
                            try:
                                v = abs(_limpar_valor(p[col_valor]))
                                if v > 0:
                                    return v
                            except:
                                pass
            return 0.0'''

c = c[:idx] + bloco_novo + c[fim:]
open(back_path, "w", encoding="utf-8").write(c)

print("\n" + "=" * 70)
print("DEFINICAO 7 CORRIGIDA")
print("=" * 70)
print(bloco_novo)

try:
    ast.parse(open(back_path, encoding="utf-8").read())
    print("\n[OK] Sintaxe validada.")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_buscar_def7_{ts}", back_path)
    print("[OK] Backup restaurado.")
