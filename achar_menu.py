import glob, os

pasta = r"pc_frontend"
print("Procurando 'Demonstrações Contábeis' nos arquivos HTML/JS:")
for arq in glob.glob(os.path.join(pasta, "**", "*.*"), recursive=True):
    if arq.endswith((".html", ".js", ".css")):
        try:
            c = open(arq, encoding="utf-8", errors="ignore").read()
            if "Demonstra" in c and "Cont" in c:
                print(f"  Encontrado em: {arq}")
        except Exception:
            pass
