import re, os

c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("VERIFICAÇÃO DA ROTA NO ARQUIVO MAIN.PY")
print("=" * 70)

if '@app.get("/gerar_pdf_centro_custos/{historico_id}")' in c:
    print("[OK] A rota ESTÁ no arquivo main.py.")
    # Mostra a definição completa
    match = re.search(r'(@app\.get\("/gerar_pdf_centro_custos/\{historico_id\}"\).*?)(?=\n@app\.|\Z)', c, re.DOTALL)
    if match:
        print("\n--- CÓDIGO DA ROTA ---")
        print(match.group(1)[:800])
else:
    print("[ERRO] A rota NÃO está no arquivo main.py.")
    print("Vamos adicioná-la novamente no final do arquivo.")

print("\n" + "=" * 70)
print("DICA: REINICIE O SERVIDOR FORÇADAMENTE")
print("=" * 70)
print("Execute o comando abaixo no terminal (pc_backend) para reiniciar:")
print("Stop-Process -Id (Get-NetTCPConnection -LocalPort 9994).OwningProcess -Force -ErrorAction SilentlyContinue")
print("Remove-Item -Recurse -Force '__pycache__' -ErrorAction SilentlyContinue")
print("..\\pc_venv\\Scripts\\python.exe -m uvicorn main:app --port 9994")
