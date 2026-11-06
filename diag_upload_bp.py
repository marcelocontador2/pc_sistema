c = open(r"pc_backend\main.py", encoding="utf-8-sig").read()

print("=" * 70)
print("1) A REGRA DO BALANCO_PATRIMONIAL ESTA NO MAIN.PY?")
print("=" * 70)
if "BALANCO_PATRIMONIAL_" in c and "nome_arquivo = f" in c:
    # Procura o trecho especifico
    idx = c.find('if tipo_relatorio and ("BALANCO_PATRIMONIAL"')
    if idx == -1:
        idx = c.find('BALANCO_PATRIMONIAL_')
    if idx != -1:
        print("[SIM] A regra existe no main.py. Trecho:")
        print(c[max(0, idx-100):idx+500])
    else:
        print("[NAO] A regra NAO foi encontrada no main.py.")
else:
    print("[NAO] A regra NAO foi encontrada no main.py.")

print("\n" + "=" * 70)
print("2) OPCOES DO DROPDOWN DE TIPO DE RELATORIO NA TELA DE IMPORTACAO")
print("=" * 70)
# Procura o index.html ou importar.html para ver as opcoes do select
import glob, os
for arq in ["pc_frontend/index.html", "pc_frontend/importar.html"]:
    if os.path.exists(arq):
        html = open(arq, encoding="utf-8", errors="ignore").read()
        print(f"\nArquivo: {arq}")
        # Procura o select de tipo_relatorio
        idx = html.find('id="tipo_relatorio"')
        if idx == -1:
            idx = html.find('name="tipo_relatorio"')
        if idx != -1:
            fim = html.find('</select>', idx) + 9
            print(html[idx:fim])
        else:
            print("  [AVISO] Select 'tipo_relatorio' nao encontrado.")
