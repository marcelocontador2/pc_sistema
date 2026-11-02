import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Padrão para encontrar o bloco try/catch interno e a declaração duplicada de msgDiv
padrao = r'let result;\s*try \{\s*result = await response\.json\(\);\s*\}\s*catch \(e\) \{\s*throw new Error\("O servidor nao retornou um JSON valido\."\);\s*\}'

novo_bloco = '''let result;
        try {
            result = await response.json();
        } catch (e) {
            throw new Error("O servidor nao retornou um JSON valido.");
        }'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, novo_bloco, c, flags=re.DOTALL)
    print("[OK] Bloco try/catch interno corrigido!")
else:
    print("[AVISO] Padrão não encontrado. Tentando substituição manual...")
    # Tenta encontrar e corrigir a indentação do catch
    c = c.replace("                    }\n catch (e) {", "        } catch (e) {")

# Remove a declaração duplicada de msgDiv (a que está dentro do if (response.ok))
c = c.replace("const msgDiv = document.getElementById('msg-upload');\nif (msgDiv) {", "if (msgDiv) {")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html corrigido!")
