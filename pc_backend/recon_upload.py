import re, os

# ===== 1. Procura /upload em TODOS os .py do projeto =====
print("=" * 70)
print("ONDE ESTA A ROTA /upload (varrendo .py do pc_sistema)")
print("=" * 70)

raiz = r"C:\Users\Marcelo Medeiros\pc_sistema"
for dirpath, dirnames, filenames in os.walk(raiz):
    # Pula venv, __pycache__, node_modules
    dirnames[:] = [d for d in dirnames if d not in ("pc_venv", "__pycache__", "node_modules", ".git")]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        caminho = os.path.join(dirpath, fn)
        try:
            txt = open(caminho, encoding="utf-8-sig").read()
        except:
            try:
                txt = open(caminho, encoding="latin-1").read()
            except:
                continue
        if '"/upload"' in txt or "'/upload'" in txt or "/upload" in txt:
            # Acha a linha
            for i, ln in enumerate(txt.splitlines(), 1):
                if "/upload" in ln:
                    rel = caminho.replace(raiz + "\\", "")
                    print(f"  {rel}:{i}: {ln.strip()[:120]}")
            # Se achou a rota, mostra o corpo
            m = re.search(r'(@\w+\.(?:post|api_route|get)\(["\'][^"\']*upload[^"\']*["\'][^)]*\)\s*\n(?:async\s+)?def\s+\w+\([^)]*\):)', txt)
            if m:
                inicio = m.end()
                # Pega até 60 linhas
                linhas = txt[inicio:].splitlines()[:60]
                print(f"  --- corpo da funcao ({fn}) ---")
                for ln in linhas:
                    print(f"      {ln}")

# ===== 2. Mostra o handler completo de upload no importar.html =====
print()
print("=" * 70)
print("importar.html - HANDLER COMPLETO do form /upload")
print("=" * 70)

html_path = r"C:\Users\Marcelo Medeiros\pc_sistema\pc_frontend\importar.html"
h = open(html_path, encoding="utf-8-sig").read()

# Acha o fetch('/upload' ... e mostra ~40 linhas ao redor
idx = h.find("/upload")
if idx == -1:
    print("  [!!] fetch /upload nao encontrado")
else:
    ini = max(0, h.rfind("\n", 0, idx - 200))
    fim = h.find("});", idx)
    if fim == -1: fim = min(len(h), idx + 2000)
    print(h[ini:fim+3])
