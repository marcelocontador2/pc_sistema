import csv, os

# Simula a funcao buscar (Definicao 7) no CSV real
caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"

def _limpar_valor(v):
    if not v: return 0.0
    v = str(v).replace("R$", "").replace("C", "").strip()
    if v in ["-", "0,00", ""]: return 0.0
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

def buscar(termo, coluna):
    termo_upper = termo.upper()
    for p in linhas:
        for col_espec in [0, 3]:
            if len(p) > col_espec and termo_upper in str(p[col_espec]).upper():
                col_valor = col_espec + 1
                if len(p) > col_valor:
                    try:
                        v = abs(_limpar_valor(p[col_valor]))
                        if v > 0:
                            return v
                    except:
                        pass
    return 0.0

# Le o CSV
linhas = []
with open(caminho, "r", encoding="latin-1", errors="ignore") as f:
    for row in csv.reader(f, delimiter=";"):
        linhas.append(row)

print("=" * 70)
print("1) TESTANDO A FUNCAO buscar COM OS TERMOS DO BP")
print("=" * 70)
print(f"buscar('TOTAL DO PASSIVO', 4) = {buscar('TOTAL DO PASSIVO', 4)}")
print(f"buscar('TOTAL DO PATRIMÔNIO LÍQUIDO', 4) = {buscar('TOTAL DO PATRIMÔNIO LÍQUIDO', 4)}")
print(f"buscar('RESULTADOS ACUMULADOS', 4) = {buscar('RESULTADOS ACUMULADOS', 4)}")

print("\n" + "=" * 70)
print("2) VERIFICANDO AS LINHAS DO CSV QUE CONTEM ESSES TERMOS")
print("=" * 70)
for i, p in enumerate(linhas):
    if len(p) > 0:
        for termo in ["TOTAL DO PASSIVO", "TOTAL DO PATRIM", "RESULTADOS ACUMULADOS"]:
            if termo.upper() in str(p[0]).upper() or (len(p) > 3 and termo.upper() in str(p[3]).upper()):
                print(f"Linha {i+1}: {p}")
                break
