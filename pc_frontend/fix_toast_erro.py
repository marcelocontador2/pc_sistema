import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Remove o alert antigo do catch e coloca uma mensagem na tabela
antigo_catch = '''alert("Aviso: " + error.message);
        
        if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';'''

novo_catch = '''// Em vez de alert, mostra o aviso direto na tabela (com estilo vermelho)
        if(tbody) tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:red; font-weight:bold; padding: 20px;">
            ⚠️ ${error.message}
        </td></tr>`;'''

js = js.replace(antigo_catch, novo_catch)

with open(path, "w", encoding="utf-8") as f:
    f.write(js)
print("OK: Alerta substituido por mensagem direta na tabela!")
