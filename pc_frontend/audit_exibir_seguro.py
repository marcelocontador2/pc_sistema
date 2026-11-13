import re
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Instalando BeautifulSoup...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

with open("composicao_receitas_despesas.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== 1. BOTOES COM TEXTO 'EXIBIR' ===")
for btn in soup.find_all("button"):
    texto = btn.get_text(strip=True)
    if "exibir" in texto.lower():
        print(f"Botao: '{texto}'")
        print(f"  onclick: {btn.get('onclick')}")
        print(f"  id: {btn.get('id')}")
        print("---")

print("\n=== 2. FUNCOES CHAMADAS PELO BOTAO ===")
for btn in soup.find_all("button"):
    texto = btn.get_text(strip=True)
    if "exibir" in texto.lower():
        oc = btn.get("onclick", "")
        if oc:
            # Extrai o nome da funcao (antes dos parenteses)
            nomes = re.findall(r'(\w+)\s*\(', oc)
            for nome in nomes:
                print(f"Funcao chamada: {nome}")
                # Procura a definicao no JS inline
                scripts = soup.find_all("script")
                for script in scripts:
                    if script.string:
                        js = script.string
                        # Padrao para function NOME(...)
                        padrao = re.compile(r'(async\s+)?function\s+' + nome + r'\s*\([^)]*\)\s*\{.*?\n\s*\}', re.DOTALL)
                        match = padrao.search(js)
                        if match:
                            print(match.group(0)[:1500])
                            print("---")
                            break

print("\n=== 3. TODAS AS CHAMADAS FETCH NO ARQUIVO ===")
for m in re.finditer(r'fetch\(\s*[`\'"]([^`\'"]+)', html):
    print(f"  - {m.group(1)}")
