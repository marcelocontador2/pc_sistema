c = open('main.py', encoding='utf-8-sig').read()

# Ajusta a função processar dentro da rota api_relatorio_centro_custos
# para ignorar o cabeçalho "Centro de Custo x Conta" e "Centro de Custo"
c = c.replace(
    'centros = [c for c in centros if c.get("nome") != "Centro de Custo"]',
    'centros = [c for c in centros if c.get("nome") not in ["Centro de Custo", "Centro de Custo x Conta"]]'
)

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] Backend ajustado para ignorar a linha 'Centro de Custo x Conta'!")
