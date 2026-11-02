import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra todas as ocorrências da definição da função (com ou sem decorator)
ocorrencias = [m.start() for m in re.finditer(r'def api_centro_custos\(periodo: str\):', c)]
print(f"Encontradas {len(ocorrencias)} definições de api_centro_custos")

if len(ocorrencias) >= 3:
    # Mantém apenas a última (a terceira)
    # Remove a primeira ocorrência (do início da função até o próximo @app ou def)
    inicio1 = c.rfind('@app.get("/api/centro_custos/{periodo}")', 0, ocorrencias[0])
    if inicio1 == -1: inicio1 = ocorrencias[0]
    fim1 = len(c)
    for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
        pos = c.find(marcador, ocorrencias[0] + 10)
        if pos != -1 and pos < fim1:
            fim1 = pos
    
    # Remove a primeira
    c = c[:inicio1] + c[fim1:]
    print("[OK] Primeira função removida!")
    
    # Recalcula as posições
    ocorrencias = [m.start() for m in re.finditer(r'def api_centro_custos\(periodo: str\):', c)]
    print(f"Agora restam {len(ocorrencias)} definições")
    
    # Remove a segunda (a que sobrou, se ainda houver 2)
    if len(ocorrencias) >= 2:
        inicio2 = c.rfind('@app.get("/api/centro_custos/{periodo}")', 0, ocorrencias[0])
        if inicio2 == -1: inicio2 = ocorrencias[0]
        fim2 = len(c)
        for marcador in ['\n@app.', '\ndef ', '\nif __name__']:
            pos = c.find(marcador, ocorrencias[0] + 10)
            if pos != -1 and pos < fim2:
                fim2 = pos
        
        c = c[:inicio2] + c[fim2:]
        print("[OK] Segunda função removida!")
    
    # Salva
    open('main.py', 'w', encoding='utf-8').write(c)
    print("[OK] main.py atualizado!")
else:
    print(f"[AVISO] Encontradas apenas {len(ocorrencias)} definições. Não foi possível remover.")
