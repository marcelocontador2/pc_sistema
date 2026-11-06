import os, glob

pasta = r"pc_storage/uploads_raw"
print("=" * 70)
print("ARQUIVOS DE BALANCO PATRIMONIAL NA PASTA")
print("=" * 70)
arquivos = glob.glob(os.path.join(pasta, "BALANCO_PATRIMONIAL_*.csv"))
if not arquivos:
    print("[ERRO] Nenhum arquivo encontrado.")
else:
    for a in arquivos:
        tamanho = os.path.getsize(a)
        data = os.path.getmtime(a)
        import datetime
        data_fmt = datetime.datetime.fromtimestamp(data).strftime("%d/%m/%Y %H:%M")
        print(f"  {a}")
        print(f"     Tamanho: {tamanho} bytes | Modificado: {data_fmt}")

print("\n" + "=" * 70)
print("TODOS OS ARQUIVOS CSV NA PASTA (para ver se tem algum novo)")
print("=" * 70)
todos = glob.glob(os.path.join(pasta, "*.csv"))
for a in todos:
    print(f"  {os.path.basename(a)}")
