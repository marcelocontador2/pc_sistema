import re

with open("conferencia.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. FUNÇÃO carregarHistorico ===")
match = re.search(r'function carregarHistorico\(\)\s*\{.*?(?=\n\s*function|\Z)', s, re.DOTALL)
if match:
    bloco = match.group(0)
    print(bloco[:1500])
    
    print("\n=== 2. VERIFICANDO ACESSO AOS DADOS DO JSON ===")
    # Procura como ele acessa os itens dentro do JSON (ex: item.periodo, item.dados)
    if "item.periodo" in bloco or "item.dados" in bloco:
        print("OK: O frontend parece estar lendo as propriedades do JSON corretamente (item.periodo, etc).")
    elif "d.periodo" in bloco or "d.dados" in bloco:
        print("OK: O frontend usa a variável 'd' para ler as propriedades do JSON.")
    else:
        print("ATENÇÃO: Não encontrei o mapeamento do JSON. Pode ser que a tabela não renderize os dados.")
else:
    print("Função não encontrada.")
