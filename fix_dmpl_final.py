import re, shutil, datetime, ast

ts = datetime.datetime.now().strftime('%H%M%S')
back_path = r"pc_backend\main.py"

shutil.copy2(back_path, f"{back_path}.bak_dmpl_final_{ts}")
c = open(back_path, encoding='utf-8-sig').read()

# Localiza o bloco do DMPL
inicio = c.find('elif tipo == "DMPL":')
if inicio == -1:
    print("[ERRO] Bloco DMPL não encontrado.")
    exit(1)

fim = c.find('else:', inicio + 10)
if fim == -1: fim = len(c)

novo_bloco = '''elif tipo == "DMPL":
            import re
            
            def buscar_valores(termo):
                """Busca o termo no CSV e retorna os dois últimos valores."""
                def normalizar(s):
                    return s.encode('ascii', 'ignore').decode('ascii').upper().strip()
                termo_norm = normalizar(termo)
                
                for linha in content.splitlines():
                    if normalizar(linha[:100]).startswith(termo_norm):
                        colunas = linha.split(';')
                        # Pega as colunas 7 (RESULTADOS ACUMULADOS) e 8 (TOTAL)
                        val1 = colunas[7].strip() if len(colunas) > 7 else ""
                        val2 = colunas[8].strip() if len(colunas) > 8 else ""
                        return val1, val2
                return "", ""
            
            # Busca os valores
            ini_1, ini_2 = buscar_valores("Saldos iniciais")
            res_1, res_2 = buscar_valores("Resultado do período")
            if not res_1 and not res_2:
                res_1, res_2 = buscar_valores("Resultado do exercício")
            fim_1, fim_2 = buscar_valores("Saldos finais")
            
            print(f"[DMPL] Saldos iniciais: {ini_1} | {ini_2}")
            print(f"[DMPL] Resultado do período: {res_1} | {res_2}")
            print(f"[DMPL] Saldos finais: {fim_1} | {fim_2}")
            
            linhas_dmpl = [
                ("Saldos iniciais", ["", "", "", "", "", "", ini_1, ini_2], True),
                ("Ajustes de exercícios anteriores", ["", "", "", "", "", "", "", "0"], False),
                ("Aumento de capital", ["", "", "", "", "", "", "", "0"], False),
                ("Resultado do exercício", ["", "", "", "", "", "", "0", "0"], False),
                ("Resultado do período", ["", "", "", "", "", "", res_1, res_2], False),
                ("Ajustes de avaliação patrimonial", ["", "", "", "", "", "", "0", "0"], False),
                ("Constituição / Reversão de reservas", ["", "", "", "", "", "", "0", "0"], False),
                ("Demais variações", ["", "", "", "", "", "", "0", "0"], False),
                ("Saldos finais", ["", "", "", "", "", "", fim_1, fim_2], True)
            ]
            for idx, (desc, valores, is_total) in enumerate(linhas_dmpl):
                row_final = [desc] + valores
                pdf.set_font("Helvetica", "B" if is_total else "", 7)
                draw_row(row_final, False, is_total, idx)
        '''

c = c[:inicio] + novo_bloco + c[fim:]
open(back_path, 'w', encoding='utf-8').write(c)
print("[OK] Bloco DMPL corrigido!")
print("-> Busca primeiro 'Resultado do período' (que tem o valor correto)")
print("-> Lê as colunas 7 e 8 do CSV (RESULTADOS ACUMULADOS e TOTAL)")

# Valida
try:
    ast.parse(open(back_path, encoding='utf-8').read())
    print("[OK] Sintaxe validada")
except SyntaxError as e:
    print(f"[ERRO] Sintaxe quebrada: {e}")
    shutil.copy2(f"{back_path}.bak_dmpl_final_{ts}", back_path)
    print("[OK] Backup restaurado")
