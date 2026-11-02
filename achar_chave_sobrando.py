with open('script_1.js', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

abre = 0
fecha = 0
for i, linha in enumerate(linhas):
    # Remove strings para não contar chaves dentro delas
    l = linha
    l = l.replace('"{', '').replace('}"', '')
    l = l.replace("'{", '').replace("}'", '')
    l = l.replace('`{', '').replace('}`', '')
    
    abre += l.count('{')
    fecha += l.count('}')
    
    # Se o número de fechamentos for maior que o de aberturas, achamos o problema
    if fecha > abre:
        print(f"⚠️ Linha {i+1}: {fecha} fechadas vs {abre} abertas. Diferença: {fecha - abre}")
        print(f"   Conteúdo: {linha.rstrip()[:120]}")
        break

print(f"\nTotal: {abre} abertas, {fecha} fechadas.")
