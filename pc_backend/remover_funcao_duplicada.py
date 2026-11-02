import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra todas as ocorrências da função api_centro_custos
ocorrencias = [m.start() for m in re.finditer(r'@app\.get\("/api/centro_custos/\{periodo\}"\)', c)]
print(f"Encontradas {len(ocorrencias)} definições da rota /api/centro_custos/{{periodo}}")

if len(ocorrencias) > 1:
    # Remove a primeira ocorrência (a antiga)
    inicio = ocorrencias[0]
    # Encontra o fim (próximo @app ou def)
    fim = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, inicio + 10)
        if pos != -1 and pos < fim:
            fim = pos
    
    c = c[:inicio] + c[fim:]
    print("[OK] Primeira função (antiga) removida!")
    
    # Salva
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] main.py atualizado!")
else:
    print("[AVISO] Só há uma definição, nada a remover.")
