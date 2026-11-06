import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_limpeza_dmpl_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Dicionário de substituições (do texto corrompido para o texto limpo)
substituicoes = {
    'Ajustes de exercÃƒÂcios anteriores': 'Ajustes de exercícios anteriores',
    'Ajustes de exercÃcios anteriores': 'Ajustes de exercícios anteriores',
    'Resultado do exercÃƒÂcio': 'Resultado do exercício',
    'Resultado do exercÃcio': 'Resultado do exercício',
    'Resultado do perÃƒÂodo': 'Resultado do período',
    'Resultado do perÃodo': 'Resultado do período',
    'Ajustes de avaliaÃƒÂ§ÃƒÂ£o patrimonial': 'Ajustes de avaliação patrimonial',
    'Ajustes de avaliaÃ§Ã£o patrimonial': 'Ajustes de avaliação patrimonial',
    'ConstituiÃƒÂ§ÃƒÂ£o / ReversÃƒÂ£o de reservas': 'Constituição / Reversão de reservas',
    'ConstituiÃ§Ã£o / ReversÃ£o de reservas': 'Constituição / Reversão de reservas',
    'Demais variaÃƒÂ§ÃƒÂµes': 'Demais variações',
    'Demais variaÃ§Ãµes': 'Demais variações'
}

# Aplica as substituições no arquivo inteiro (isso vai pegar as linhas da tabela DMPL)
for antigo, novo in substituicoes.items():
    if antigo in c:
        c = c.replace(antigo, novo)
        print(f"[OK] Corrigido: {antigo} -> {novo}")

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("\n[OK] Sintaxe validada com sucesso.")
except SyntaxError as e:
    print(f"\n[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_limpeza_dmpl_{ts}", back_path)
    print("[OK] Backup restaurado")
