import os

pasta = r"pc_frontend"
arquivos = [f for f in os.listdir(pasta) if "relatorio_comparativo_despesas" in f.lower() and f.endswith(".html")]

print("=" * 70)
print("ARQUIVOS DE RELATÓRIO DE DESPESAS NA PASTA")
print("=" * 70)

for f in arquivos:
    caminho = os.path.join(pasta, f)
    tamanho = os.path.getsize(caminho)
    import datetime
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
    print(f"  {f} ({tamanho:,} bytes) - modificado {mtime.strftime('%d/%m/%Y %H:%M')}")

if not arquivos:
    print("  [ERRO] Nenhum arquivo encontrado!")

# Verifica o que a rota procura
print("\n" + "=" * 70)
print("VERIFICANDO A ROTA /relatorio_comparativo_despesas_v2")
print("=" * 70)

c_back = open(r"pc_backend\main.py", encoding='utf-8-sig').read()
idx = c_back.find('@app.get("/relatorio_comparativo_despesas_v2")')
if idx != -1:
    print(c_back[idx:idx+600])
else:
    print("[AVISO] Rota não encontrada no main.py")
