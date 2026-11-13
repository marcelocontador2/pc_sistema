import os

upload_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_storage\uploads_raw"

print("=" * 80)
print(f"📁 Conteúdo da pasta: {upload_dir}")
print("=" * 80)

if not os.path.exists(upload_dir):
    print("❌ A pasta não existe!")
    exit()

arquivos = os.listdir(upload_dir)
csvs = [a for a in arquivos if a.lower().endswith(".csv")]

print(f"Total de arquivos: {len(arquivos)}")
print(f"Total de CSVs: {len(csvs)}")
print()

print("📄 Arquivos CSV encontrados:")
for a in sorted(csvs):
    tamanho = os.path.getsize(os.path.join(upload_dir, a))
    print(f"   - {a} ({tamanho} bytes)")

print()
print("=" * 80)
print("🔍 Procurando arquivos que contenham 'COMPARATIVO_RECEITAS':")
print("=" * 80)
for a in sorted(arquivos):
    if "COMPARATIVO" in a.upper() and "RECEITA" in a.upper():
        print(f"   ✅ {a}")

print()
print("=" * 80)
print("🧪 Teste: qual arquivo seria escolhido para o período '2026-TRIMESTRE-3'?")
print("=" * 80)
periodo = "2026-TRIMESTRE-3"
periodo_formatado = periodo.replace("-", "_")
arquivo_esperado = os.path.join(upload_dir, f"COMPARATIVO_RECEITAS_{periodo_formatado}.csv")
print(f"Nome esperado exato: COMPARATIVO_RECEITAS_{periodo_formatado}.csv")
print(f"Existe? {os.path.exists(arquivo_esperado)}")

if not os.path.exists(arquivo_esperado):
    print("\n🔎 Buscando por aproximação (contém 'COMPARATIVO_RECEITAS' e o período):")
    for a in arquivos:
        if periodo_formatado in a and "COMPARATIVO_RECEITAS" in a:
            print(f"   ⚠️ Match aproximado: {a}")
