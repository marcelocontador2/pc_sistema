import csv

caminho = r"pc_storage/uploads_raw/BALANCO_PATRIMONIAL_2026_TRIMESTRE_3.csv"
linhas = []
with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
    linhas = [row for row in csv.reader(f, delimiter=';')]

print("=" * 70)
print("TODAS AS LINHAS ONDE p[0] CONTEM 'TOTAL'")
print("=" * 70)
for i, p in enumerate(linhas, 1):
    if len(p) > 0 and 'TOTAL' in str(p[0]).upper():
        print(f"Linha {i}: len={len(p)}, p[0]={repr(p[0])}, p[1]={repr(p[1]) if len(p)>1 else ''}, p[3]={repr(p[3]) if len(p)>3 else ''}, p[4]={repr(p[4]) if len(p)>4 else ''}")
