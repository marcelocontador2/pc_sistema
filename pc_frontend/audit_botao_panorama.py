import re

with open("panorama.html", "r", encoding="utf-8") as f:
    s = f.read()

print("=== 1. BOTAO VERIFICAR ===")
btn = re.search(r'<button[^>]*>([^<]*Verificar[^<]*)</button>', s)
if btn:
    print(btn.group(0))
else:
    print("Botao nao encontrado.")

print("\n=== 2. FUNCAO carregarPanorama() ===")
match = re.search(r'(async\s+)?function\s+carregarPanorama\(\)\s*\{.*?\n\}', s, re.DOTALL)
if match:
    print(match.group(0)[:2000])
else:
    print("Funcao nao encontrada.")

print("\n=== 3. O BOTAO TEM ONCLICK? ===")
if 'onclick="carregarPanorama()"' in s:
    print("SIM, o botao chama carregarPanorama() via onclick.")
else:
    print("NAO, o botao nao tem onclick='carregarPanorama()'. Pode ser que o event listener esteja faltando.")

print("\n=== 4. O SCRIPT ESTA NO LUGAR CERTO? ===")
pos_script = s.find("<script>")
pos_body = s.find("</body>")
if pos_script != -1 and pos_body != -1:
    print(f"Script em: {pos_script}, Body em: {pos_body}.")
    if pos_script < pos_body:
        print("OK: Script esta antes do </body>.")
    else:
        print("ERRO: Script esta DEPOIS do </body>.")
else:
    print("Script ou body nao encontrados.")
