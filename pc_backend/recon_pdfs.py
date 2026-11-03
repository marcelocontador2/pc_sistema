import re, os

c = open("main.py", encoding="utf-8-sig").read()
print("=" * 70)
print("ROTAS DE GERAÇÃO DE PDF ENCONTRADAS NO SISTEMA")
print("=" * 70)

rotas = re.findall(r'@app\.get\(["\'](/gerar_pdf_[^"\']+)["\']\)\s*\ndef\s+(\w+)\(([^)]*)\)', c)
for rota, func, args in rotas:
    print(f"Rota: {rota:45} | Função: {func:35} | Parâmetros: {args}")

print("\n" + "=" * 70)
print("ARQUIVOS HTML NA PASTA FRONTEND QUE MENCIONAM 'gerar_pdf'")
print("=" * 70)

front_dir = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend"
for f in os.listdir(front_dir):
    if f.endswith(".html"):
        caminho = os.path.join(front_dir, f)
        try:
            html = open(caminho, encoding="utf-8-sig").read()
            if "gerar_pdf" in html:
                print(f" - {f}")
        except:
            pass
