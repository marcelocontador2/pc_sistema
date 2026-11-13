path = "liquidez.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# Encontra o inicio da funcao
inicio = s.find("function renderizarResultado")
if inicio == -1:
    print("Funcao nao encontrada!")
else:
    # Conta as chaves para achar o fim da funcao
    nivel = 0
    fim = -1
    for i in range(inicio, len(s)):
        if s[i] == '{':
            nivel += 1
        elif s[i] == '}':
            nivel -= 1
            if nivel == 0:
                fim = i + 1
                break
                
    if fim != -1:
        print("=== FUNCAO COMPLETA ===")
        print(s[inicio:fim])
    else:
        print("Nao foi possivel encontrar o fim da funcao.")
