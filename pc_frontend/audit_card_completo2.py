path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

inicio = s.find('<div class="card">')
if inicio != -1:
    # Conta as divs para achar o fechamento
    nivel = 0
    fim = -1
    i = inicio
    while i < len(s):
        if s[i:i+5] == '<div ':
            nivel += 1
        elif s[i:i+6] == '</div>':
            nivel -= 1
            if nivel == 0:
                fim = i + 6
                break
        i += 1
        
    if fim != -1:
        print("=== CARD COMPLETO ===")
        print(s[inicio:fim])
    else:
        print("Nao foi possivel encontrar o fechamento do card.")
else:
    print("Card nao encontrado.")
