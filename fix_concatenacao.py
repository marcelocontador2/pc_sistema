p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()
old = """        + html_itens_declaracao
        '<div style="margin-top: 50px; text-align: center;">'"""
new = """        + html_itens_declaracao
        + '<div style="margin-top: 50px; text-align: center;">'"""
if old not in s:
    print('ERRO: padrao nao encontrado')
    raise SystemExit(1)
s = s.replace(old, new, 1)
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('OK: + adicionado antes do div margin-top:50px')
