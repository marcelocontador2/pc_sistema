import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Corrige os onclick quebrados (remove a verificação com aspas erradas)
html = re.sub(r'onclick="if\(typeof exibirSelecionado[^>]+"', 'onclick="exibirSelecionado()"', html)
html = re.sub(r'onclick="if\(typeof excluirSelecionado[^>]+"', 'onclick="excluirSelecionado()"', html)
html = re.sub(r'onclick="if\(typeof salvarPanorama[^>]+"', 'onclick="salvarPanorama()"', html)

# 2. Checa a integridade do JavaScript
scripts = re.findall(r'<script.*?>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
tem_erro = False

for i, script in enumerate(scripts):
    if 'function carregarPanorama' in script or 'function salvarPanorama' in script:
        # Checa chaves { } desbalanceadas
        if script.count('{') != script.count('}'):
            print(f"[ALERTA] Bloco JS {i+1}: Chaves desbalanceadas ({script.count('{')} x {script.count('}')}).")
            tem_erro = True
        # Checa template literals (crases `) soltos, que costumam travar a pagina toda
        if script.count('`') % 2 != 0:
            print(f"[ALERTA] Bloco JS {i+1}: Crases (`) desbalanceadas. Isso trava a pagina!")
            tem_erro = True

if tem_erro:
    print("[AVISO] Foram encontrados possiveis erros no JavaScript.")
else:
    print("[OK] Nenhum erro estrutural grave encontrado no JavaScript.")

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("\n[OK] Arquivo panorama.html corrigido e salvo.")
print("\n=== PROXIMO PASSO ===")
print("1. O servidor NAO precisa ser reiniciado.")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R (ou Ctrl + F5) para limpar o cache.")
print("4. Teste os botoes.")
