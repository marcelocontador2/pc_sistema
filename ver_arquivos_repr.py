import os

pasta = r"pc_storage/uploads_raw"
print("=" * 70)
print("TODOS OS ARQUIVOS NA PASTA (incluindo nomes com espacos)")
print("=" * 70)
for a in os.listdir(pasta):
    caminho = os.path.join(pasta, a)
    if os.path.isfile(caminho):
        print(f"  {repr(a)} | Tamanho: {os.path.getsize(caminho)} bytes")
