import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o trecho do .catch() da funcao carregar() para mostrar um alerta amigavel
# e limpar a tabela.
antigo_catch = '''.catch(e => {
            console.error(e);
            if(tbody) tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:red;">${e.message}</td></tr>`;
        });'''

novo_catch = '''.catch(e => {
            console.error(e);
            // Mostra um alerta amigavel para o usuario
            alert("Não há dados disponíveis para o período selecionado (" + periodoFormatado + ").\\n\\nVerifique se o arquivo CSV foi importado corretamente.");
            
            // Limpa a tabela e o grafico
            if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
            if (window._chartDMPL) {
                window._chartDMPL.destroy();
                window._chartDMPL = null;
            }
        });'''

# Como a funcao carregar tem a mesma estrutura de catch, vamos substituir apenas no bloco dela
# Primeiro, isolamos o bloco da funcao carregar
padrao_carregar = re.compile(r'(function carregar\(\)\s*\{.*?\n\})', re.DOTALL)
match = padrao_carregar.search(js)

if match:
    bloco_carregar = match.group(1)
    novo_bloco = bloco_carregar.replace(antigo_catch, novo_catch)
    
    js = js.replace(bloco_carregar, novo_bloco)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK: Funcao carregar() atualizada para avisar quando o periodo nao existir!")
else:
    print("AVISO: Funcao carregar() nao encontrada no arquivo JS.")
