c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

# Procura o formulario de upload
idx = c.find('id="upload-tipo"')
if idx != -1:
    # Volta para achar o <form> ou a funcao de upload
    print("=" * 70)
    print("FORMULARIO DE UPLOAD (trecho ao redor do select)")
    print("=" * 70)
    print(c[max(0, idx-500):idx+1500])
else:
    print("[ERRO] Select 'upload-tipo' nao encontrado.")
