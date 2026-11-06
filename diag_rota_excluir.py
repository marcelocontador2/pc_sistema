c = open("pc_backend/main.py", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) ROTAS QUE CONTÊM 'excluir' NO CAMINHO")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if '@app' in ln and ('excluir' in ln.lower() or 'delete' in ln.lower()):
        print(f"  Linha {i}: {ln.strip()}")

print("\n" + "=" * 70)
print("2) FUNÇÕES QUE CONTÊM 'excluir' NO NOME")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'def ' in ln and 'excluir' in ln.lower():
        print(f"  Linha {i}: {ln.strip()}")
        
print("\n" + "=" * 70)
print("3) ONDE OS ARQUIVOS SÃO SALVOS (UPLOAD)")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'upload' in ln.lower() and ('file' in ln.lower() or 'save' in ln.lower() or 'path' in ln.lower()):
        print(f"  Linha {i}: {ln.strip()[:100]}")
