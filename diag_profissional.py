import ast, os, subprocess, json

print("=" * 70)
print("1) VERIFICANDO O CODIGO DA ROTA /upload (versao atual)")
print("=" * 70)
c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()
idx = c.find('async def upload_arquivo(')
if idx == -1:
    print("[ERRO] Funcao nao encontrada.")
else:
    fim = c.find('@app', idx + 20)
    if fim == -1: fim = len(c)
    trecho = c[idx:fim]
    
    # Conta linhas
    linhas = trecho.split("\n")
    print(f"Tamanho da funcao: {len(linhas)} linhas")
    
    # Verifica se tem try/except (que pode estar mascarando erro)
    if "try:" in trecho:
        print("[AVISO] A funcao tem 'try:' (pode estar mascarando erro).")
    if "except" in trecho:
        print("[AVISO] A funcao tem 'except' (pode estar engolindo excecao).")
    
    # Verifica se tem o return
    if 'return {"ok": True' in trecho:
        print("[OK] A funcao tem 'return' antecipado.")
    else:
        print("[PROBLEMA] A funcao NAO tem 'return' antecipado.")
    
    # Verifica se tem print de debug
    if 'print(' in trecho:
        print("[OK] A funcao tem 'print' de debug (vamos ver no terminal).")
    else:
        print("[AVISO] A funcao NAO tem 'print' de debug.")

print("\n" + "=" * 70)
print("2) PROCESSOS PYTHON RODANDO (quantos e quais)")
print("=" * 70)
try:
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"], capture_output=True, text=True, timeout=10)
    linhas = result.stdout.strip().split("\n")
    print(f"Total de processos python.exe: {len(linhas) - 1}")
    for ln in linhas[1:]:
        print(f"  {ln.strip()}")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("3) O QUE ESTA NA PORTA 9994")
print("=" * 70)
try:
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
    for ln in result.stdout.split("\n"):
        if ":9994" in ln and "LISTENING" in ln:
            print(f"  {ln.strip()}")
except Exception as e:
    print(f"[ERRO] {e}")

print("\n" + "=" * 70)
print("4) MIDDLEWARES QUE PODEM BLOQUEAR A REQUISICAO")
print("=" * 70)
if "@app.middleware" in c:
    print("[AVISO] Existe middleware no main.py! Pode estar bloqueando.")
    for i, ln in enumerate(c.split("\n"), 1):
        if "@app.middleware" in ln:
            print(f"  Linha {i}: {ln.strip()}")
else:
    print("[OK] Nenhum middleware encontrado.")
