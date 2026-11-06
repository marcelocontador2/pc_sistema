c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

# Localiza a rota do PDF do BP
idx = c.find('@app.get("/gerar_pdf_analise_bp/{id}")')
if idx == -1:
    print("[ERRO] Rota do PDF do BP nao encontrada.")
else:
    fim = c.find('@app', idx + 10)
    if fim == -1:
        fim = len(c)
    bloco = c[idx:fim]

    print("=" * 70)
    print("TRECHO DO PDF DO BP (onde os valores sao formatados)")
    print("=" * 70)
    # Mostra as linhas que tem 'fmt', 'f"R$', 'multi_cell', 'cell'
    linhas = bloco.split("\n")
    for i, ln in enumerate(linhas, 1):
        if 'fmt' in ln or 'R$' in ln or 'multi_cell' in ln or 'cell(' in ln:
            print(f"  {i}: {ln.strip()[:150]}")

    print("\n" + "=" * 70)
    print("FUNCAO fmt NO BLOCO (se existir)")
    print("=" * 70)
    idx_fmt = bloco.find('def fmt(')
    if idx_fmt != -1:
        fim_fmt = bloco.find('\n\n', idx_fmt)
        if fim_fmt == -1:
            fim_fmt = idx_fmt + 500
        print(bloco[idx_fmt:fim_fmt])
    else:
        print("[AVISO] Funcao fmt NAO encontrada no bloco do PDF.")
