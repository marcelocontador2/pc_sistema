import os, glob, datetime

pasta = r"pc_storage/uploads_raw"
print("=" * 70)
print("TODOS OS ARQUIVOS NA PASTA (com data de modificacao)")
print("=" * 70)
arquivos = glob.glob(os.path.join(pasta, "*.*"))
if not arquivos:
    print("[ERRO] Nenhum arquivo encontrado.")
else:
    for a in sorted(arquivos, key=os.path.getmtime, reverse=True):
        data = datetime.datetime.fromtimestamp(os.path.getmtime(a)).strftime("%d/%m/%Y %H:%M")
        tamanho = os.path.getsize(a)
        print(f"  {os.path.basename(a)}")
        print(f"     Modificado: {data} | Tamanho: {tamanho} bytes")
