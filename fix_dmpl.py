import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza o bloco do DMPL
inicio = c.find('elif tipo == "DMPL":')
if inicio == -1:
    print("[ERRO] Bloco do DMPL não encontrado.")
    exit(1)

# Encontra o fim do bloco (próximo 'elif' ou 'else')
fim = c.find('else:', inicio + 10)
if fim == -1: fim = len(c)

bloco_antigo = c[inicio:fim]

# Novo bloco com a busca corrigida
novo_bloco = '''elif tipo == "DMPL":
            import re
            def buscar_valores(termo):
                # Normaliza o termo para busca (remove acentos)
                def normalizar(s):
                    return s.encode('ascii', 'ignore').decode('ascii').upper().strip()
                termo_norm = normalizar(termo)
                
                for linha in content.splitlines():
                    linha_norm = normalizar(linha)
                    if termo_norm in linha_norm:
                        colunas = linha.split(';')
                        matches = re.findall(r'(?<![\\d,])(-?\\d{1,3}(?:\\.\\d{3})*,\\d{2}|-?\\d+)(?![\\d,])', ";".join(colunas))
                        if len(matches) >= 2: return matches[-2], matches[-1]
                        elif len(matches) == 1: return "", matches[-1]
                return "", ""
            
            # Termos de busca (sem acento, para bater com o CSV corrompido)
            ini_1, ini_2 = buscar_valores("Saldos iniciais")
            res_1, res_2 = buscar_valores("Resultado do periodo")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercicio")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado")
            fim_1, fim_2 = buscar_valores("Saldos finais")
            
            linhas_dmpl = [
                ("Saldos iniciais", ["", "", "", "", "", "", ini_1, ini_2], True),
                ("Ajustes de exercicios anteriores", ["", "", "", "", "", "", "", "0"], False),
                ("Aumento de capital", ["", "", "", "", "", "", "", "0"], False),
                ("Resultado do exercicio", ["", "", "", "", "", "", "0", "0"], False),
                ("Resultado do periodo", ["", "", "", "", "", "", res_1, res_2], False),
                ("Ajustes de avaliacao patrimonial", ["", "", "", "", "", "", "0", "0"], False),
                ("Constituicao / Reversao de reservas", ["", "", "", "", "", "", "0", "0"], False),
                ("Demais variacoes", ["", "", "", "", "", "", "0", "0"], False),
                ("Saldos finais", ["", "", "", "", "", "", fim_1, fim_2], True)
            ]
            for idx, (desc, valores, is_total) in enumerate(linhas_dmpl):
                row_final = [desc] + valores
                pdf.set_font("Helvetica", "B" if is_total else "", 7)
                draw_row(row_final, False, is_total, idx)
        '''

c = c[:inicio] + novo_bloco + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)
print("[OK] Bloco do DMPL corrigido para buscar 'Resultado do periodo' mesmo com encoding corrompido.")

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_{ts}", back_path)
    print("[OK] Backup restaurado")
