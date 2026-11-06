import shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_tabela_dmpl_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Vamos localizar o inicio da lista linhas_dmpl e o fim dela (que termina com "Saldos finais")
inicio_marcador = 'linhas_dmpl = ['
fim_marcador = '("Saldos finais", ["", "", "", "", "", "", fim_1, fim_2], True)\n            ]'

idx_inicio = c.find(inicio_marcador)
idx_fim = c.find(fim_marcador, idx_inicio)

if idx_inicio == -1 or idx_fim == -1:
    print("[ERRO] Nao foi possivel localizar o bloco linhas_dmpl no arquivo.")
    exit(1)

idx_fim += len(fim_marcador)

# Criamos a nova lista usando a funcao chr() para os acentos, assim o terminal nao corrompe
# "ç" = chr(231), "ã" = chr(227), "í" = chr(237), "ó" = chr(243), "õ" = chr(245)
c_cedilha = chr(231)
a_til = chr(227)
i_agudo = chr(237)
o_agudo = chr(243)
o_til = chr(245)
a_agudo = chr(225)
e_agudo = chr(233)
a_circ = chr(226)

t_exercicios = f"exerc{i_agudo}cios"
t_exercicio = f"exerc{i_agudo}cio"
t_periodo = f"per{i_agudo}odo"
t_avaliacao = f"avalia{c_cedilha}{a_til}o"
t_constituicao = f"Constitui{c_cedilha}{a_til}o"
t_reversao = f"Revers{a_til}o"
t_variacoes = f"varia{c_cedilha}{o_til}es"

nova_lista = f'''linhas_dmpl = [
                ("Saldos iniciais", ["", "", "", "", "", "", ini_1, ini_2], True),
                ("Ajustes de {t_exercicios} anteriores", ["", "", "", "", "", "", "", "0"], False),
                ("Aumento de capital", ["", "", "", "", "", "", "", "0"], False),
                ("Resultado do {t_exercicio}", ["", "", "", "", "", "", "0", "0"], False),
                ("Resultado do {t_periodo}", ["", "", "", "", "", "", res_1, res_2], False),
                ("Ajustes de {t_avaliacao} patrimonial", ["", "", "", "", "", "", "0", "0"], False),
                ("{t_constituicao} / {t_reversao} de reservas", ["", "", "", "", "", "", "0", "0"], False),
                ("Demais {t_variacoes}", ["", "", "", "", "", "", "0", "0"], False),
                ("Saldos finais", ["", "", "", "", "", "", fim_1, fim_2], True)
            ]'''

# Substitui o bloco antigo pelo novo
c = c[:idx_inicio] + nova_lista + c[idx_fim:]

open(back_path, 'w', encoding='utf-8').write(c)

# Valida sintaxe
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada com sucesso.")
    print("[OK] Bloco da tabela DMPL substituido com textos limpos.")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_tabela_dmpl_{ts}", back_path)
    print("[OK] Backup restaurado")
