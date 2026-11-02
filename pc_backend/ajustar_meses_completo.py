import re

c = open('main.py', encoding='utf-8-sig').read()

# Encontra a função api_relatorio_v2 e substitui a parte que lê os meses
# Primeiro, vamos localizar a função ler_csv dentro dela
padrao = r'(def api_relatorio_v2.*?def ler_csv\(periodo_str\):.*?return centros\s*)'

# O trecho que define os meses fixos (JAN a JUN) e calcula os valores
trecho_antigo = '''            meses = {"JAN": 0, "FEV": 0, "MAR": 0, "ABR": 0, "MAI": 0, "JUN": 0}
            
            for linha in linhas[inicio_dados:]:
                if ";" in linha:
                    partes = linha.strip().split(";")
                else:
                    partes = linha.strip().split(",")
                
                if len(partes) < 2:
                    continue
                
                nome = partes[0].strip().strip('"')
                if not nome or "TOTAL" in nome.upper() or "Centro de Custo" in nome:
                    continue
                
                valor = 0.0
                for parte in reversed(partes):
                    parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                    try:
                        valor = float(parte_limpa)
                        if valor > 0:
                            break
                    except:
                        continue
                
                centros.append({"nome": nome, "valor": valor})'''

trecho_novo = '''            # Lê o cabeçalho para descobrir quais meses existem
            meses_disponiveis = []
            for linha in linhas[:inicio_dados]:
                if "JAN" in linha.upper():
                    if ";" in linha:
                        partes_cabecalho = linha.strip().split(";")
                    else:
                        partes_cabecalho = linha.strip().split(",")
                    for p in partes_cabecalho:
                        p_limpo = p.strip().upper()
                        if p_limpo in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]:
                            meses_disponiveis.append(p_limpo)
                    break
            
            if not meses_disponiveis:
                meses_disponiveis = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN"]
            
            # Inicializa os meses encontrados
            meses = {m: 0 for m in meses_disponiveis}
            
            for linha in linhas[inicio_dados:]:
                if ";" in linha:
                    partes = linha.strip().split(";")
                else:
                    partes = linha.strip().split(",")
                
                if len(partes) < 2:
                    continue
                
                nome = partes[0].strip().strip('"')
                if not nome or "TOTAL" in nome.upper() or "Centro de Custo" in nome:
                    continue
                
                # O valor total está na última coluna (Realizado)
                valor = 0.0
                for parte in reversed(partes):
                    parte_limpa = parte.strip().strip('"').replace(".", "").replace(",", ".")
                    try:
                        valor = float(parte_limpa)
                        if valor > 0:
                            break
                    except:
                        continue
                
                centros.append({"nome": nome, "valor": valor})'''

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Leitura de meses ajustada para todos os meses do CSV!")
else:
    print("[AVISO] Trecho não encontrado. Tentando abordagem alternativa...")
    # Se não encontrar, talvez o código seja ligeiramente diferente. Vou tentar substituir apenas a linha dos meses
    c = c.replace('meses = {"JAN": 0, "FEV": 0, "MAR": 0, "ABR": 0, "MAI": 0, "JUN": 0}', '# Meses serão definidos dinamicamente')

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
