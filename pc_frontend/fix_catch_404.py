import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o .catch() da funcao carregar()
# Vamos isolar o bloco da funcao carregar e trocar o catch dela
padrao_carregar = re.compile(r'(function carregar\(\)\s*\{.*?)(\.catch\(e\s*=>\s*\{.*?\}\);)(\s*\})', re.DOTALL)

def substituir_catch(match):
    inicio = match.group(1)
    fim_funcao = match.group(3)
    
    novo_catch = '''.catch(err => {
            // O backend retorna 404 quando nao encontra o arquivo, com a mensagem no corpo
            let mensagem = "Erro ao verificar dados.";
            
            // Como o fetch joga o 404 no catch, nao temos acesso direto ao body aqui de forma sincrona.
            // A melhor forma e interceptar antes. Vamos reescrever a chamada do fetch para tratar isso.
            console.error(err);
        });'''
    
    # Em vez de apenas trocar o catch, vamos reescrever a chamada do fetch inteira
    # para tratar o 404 manualmente antes do .then
    novo_fetch = '''.then(r => {
            if (r.status === 404) {
                return r.json().then(errData => {
                    throw new Error(errData.mensagem || "Arquivo não encontrado para este período.");
                });
            }
            if (!r.ok) {
                throw new Error("Erro HTTP " + r.status);
            }
            return r.json();
        })'''
    
    # Substitui o .then(r => r.json()) pelo novo tratamento
    inicio = inicio.replace(".then(r => r.json())", novo_fetch)
    
    return inicio + '''.catch(e => {
            alert("Aviso: " + e.message);
            if(tbody) tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
            if (window._chartDMPL) { window._chartDMPL.destroy(); window._chartDMPL = null; }
        });''' + fim_funcao

nova_js, n = padrao_carregar.subn(substituir_catch, js)

if n > 0:
    with open(path, "w", encoding="utf-8") as f:
        f.write(nova_js)
    print("OK: Funcao carregar() ajustada para capturar a mensagem do 404!")
else:
    print("AVISO: Nao foi possivel encontrar a funcao carregar para substituir.")
