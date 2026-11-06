import ast, re

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) A ROTA /upload EXISTE? QUANTAS VEZES?")
print("=" * 70)
ocorrencias = [(i, ln.strip()) for i, ln in enumerate(c.split("\n"), 1) if '@app.post("/upload")' in ln]
if not ocorrencias:
    print("[ERRO] A rota @app.post('/upload') NAO EXISTE no main.py!")
else:
    for linha, txt in ocorrencias:
        print(f"  Linha {linha}: {txt}")

print("\n" + "=" * 70)
print("2) A ROTA /upload ESTA DUPLICADA? (causa o travamento)")
print("=" * 70)
print(f"Total de rotas /upload: {len(ocorrencias)}")
if len(ocorrencias) > 1:
    print("[PROBLEMA] Existem rotas /upload DUPLICADAS! Isso causa conflito e travamento.")
else:
    print("[OK] Apenas 1 rota /upload.")

print("\n" + "=" * 70)
print("3) A FUNCAO upload_arquivo ESTA COM RETURN ANTECIPADO?")
print("=" * 70)
idx = c.find("async def upload_arquivo")
if idx != -1:
    # Pega as primeiras 60 linhas da funcao
    trecho = c[idx:idx+3000]
    if 'return {"ok": True' in trecho:
        print("[OK] A funcao tem 'return' antecipado.")
    else:
        print("[PROBLEMA] A funcao NAO tem 'return' antecipado (vai processar o CSV e travar).")
    
    # Mostra a estrutura basica
    print("\nEstrutura da funcao (primeiras 30 linhas):")
    linhas = trecho.split("\n")
    for i, ln in enumerate(linhas[:30]):
        print(f"  {i+1}: {ln}")

print("\n" + "=" * 70)
print("4) O ARQUIVO main.py TEM SINTAXE VALIDA?")
print("=" * 70)
try:
    ast.parse(c)
    print("[OK] Sintaxe valida.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    print(f"Linha do erro: {e.lineno}")

print("\n" + "=" * 70)
print("5) O QUE ESTA RODANDO NA PORTA 9994?")
print("=" * 70)
import subprocess
try:
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
    for ln in result.stdout.split("\n"):
        if ":9994" in ln:
            print(f"  {ln.strip()}")
except Exception as e:
    print(f"[ERRO] {e}")
