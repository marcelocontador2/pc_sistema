c = open("pc_backend/main.py", encoding="utf-8-sig").read()
idx = c.find("async def salvar_integridade_matriz")
if idx != -1:
    fim = c.find("@app", idx + 10)
    if fim == -1:
        fim = idx + 2000
    print("Funcao salvar_integridade_matriz no main.py:")
    print(c[idx:fim])
else:
    print("[AVISO] Funcao nao encontrada no main.py.")
