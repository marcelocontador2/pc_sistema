c = open("pc_frontend/index.html", encoding="utf-8", errors="ignore").read()

print("=" * 70)
print("1) FUNCAO enviarArquivo (codigo completo)")
print("=" * 70)
idx = c.find("async function enviarArquivo")
if idx == -1:
    idx = c.find("function enviarArquivo")
if idx != -1:
    # Pega ate o proximo function ou fim do script
    fim = c.find("function ", idx + 30)
    if fim == -1:
        fim = c.find("</script>", idx)
    if fim != -1:
        print(c[idx:fim])
    else:
        print(c[idx:idx+3000])
else:
    print("[ERRO] Funcao enviarArquivo nao encontrada.")

print("\n" + "=" * 70)
print("2) BOTAO DE ENVIO (onclick / type)")
print("=" * 70)
for i, ln in enumerate(c.split("\n"), 1):
    if 'type="submit"' in ln or 'type="button"' in ln or 'onclick' in ln:
        if 'upload' in ln.lower() or 'enviar' in ln.lower() or 'import' in ln.lower():
            print(f"  Linha {i}: {ln.strip()[:150]}")

print("\n" + "=" * 70)
print("3) FORM DE UPLOAD (id, onsubmit, action)")
print("=" * 70)
idx = c.find('id="form-upload"')
if idx != -1:
    print(c[max(0, idx-200):idx+1000])
else:
    print("[ERRO] Form 'form-upload' nao encontrado.")

print("\n" + "=" * 70)
print("4) INPUT DE ARQUIVO (id, aceita)")
print("=" * 70)
idx = c.find('id="upload-arquivo"')
if idx != -1:
    print(c[max(0, idx-100):idx+500])
else:
    print("[ERRO] Input 'upload-arquivo' nao encontrado.")
