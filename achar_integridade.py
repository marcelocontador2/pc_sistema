import glob, os
arquivos = glob.glob("pc_backend/**/integridade.py", recursive=True)
if not arquivos:
    print("[ERRO] Arquivo integridade.py nao encontrado.")
else:
    for a in arquivos:
        print(f"  {a}")
