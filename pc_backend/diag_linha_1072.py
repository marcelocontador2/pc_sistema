c = open("main.py", encoding="utf-8-sig").read()
linhas = c.split("\n")

# Linha 1072 (indice 1071)
alvo = linhas[1071]
print("Linha 1072 inteira:")
print(repr(alvo))
print("\nCodigos Unicode dos caracteres da parte 'PATRIM...':")

# Localiza o trecho "PATRIM"
idx = alvo.find("PATRIM")
if idx == -1:
    print("[AVISO] 'PATRIM' nao encontrado na linha.")
else:
    trecho = alvo[idx:idx+30]
    for ch in trecho:
        print(f"  {repr(ch)}  U+{ord(ch):04X}")

# Tambem mostra o trecho "QUIDO"
idx2 = alvo.find("QUIDO")
if idx2 != -1:
    print("\nCodigos do trecho 'L...QUIDO':")
    trecho2 = alvo[max(0,idx2-4):idx2+6]
    for ch in trecho2:
        print(f"  {repr(ch)}  U+{ord(ch):04X}")
