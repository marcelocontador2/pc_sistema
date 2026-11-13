import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Encontra o bloco .then(retorno => { ... }) da funcao carregar
padrao = re.compile(r'(function carregar\(\)\s*\{.*?\.then\(retorno\s*=>\s*\{.*?)(// O backend pode retornar)', re.DOTALL)

# Vamos inserir uma verificacao logo no inicio do .then
novo_codigo = r'''\1
            // Verifica se o backend avisou que o arquivo nao existe (mesmo que o status HTTP seja 200)
            if (retorno && retorno.erro) {
                alert("Aviso: " + (retorno.mensagem || "Não há dados para o período selecionado."));
                if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
                if (window._chartDMPL) { window._chartDMPL.destroy(); window._chartDMPL = null; }
                return; // Para a execucao aqui
            }

            \2'''

nova_js, n = padrao.subn(novo_codigo, js)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_js)
    print("OK: Verificacao adicionada! O alerta vai aparecer quando o backend retornar erro:true.")
else:
    print("AVISO: Nao foi possivel encontrar o bloco .then() da funcao carregar.")
