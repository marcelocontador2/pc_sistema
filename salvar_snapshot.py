import os, shutil, datetime

# Define a pasta do snapshot com data e hora
data_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
pasta_backup = f"_backups_arquivo\\SNAPSHOT_LIQUIDEZ_OK_{data_hora}"

os.makedirs(pasta_backup, exist_ok=True)

arquivos = [
    "pc_backend\\main.py",
    "pc_frontend\\liquidez.html"
]

print(f"Criando snapshot em: {pasta_backup}\n")

for arq in arquivos:
    if os.path.exists(arq):
        destino = os.path.join(pasta_backup, os.path.basename(arq))
        shutil.copy2(arq, destino)
        print(f"[OK] Salvo: {destino}")
    else:
        print(f"[ERRO] Nao encontrado: {arq}")

print("\n=== SNAPSHOT CONCLUIDO COM SUCESSO! ===")
print("Se algo quebrar no futuro, basta copiar esses dois arquivos de volta para as pastas originais.")
