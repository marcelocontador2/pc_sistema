import re

path = "analise_dmpl.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# 1. Adiciona uma div de aviso (invisivel por padrao) logo apos o titulo
if 'id="aviso-erro"' not in s:
    # Encontra o titulo da pagina para colocar o aviso logo abaixo
    titulo = re.search(r'(<h[12][^>]*>.*?DMPL.*?</h[12]>)', s, re.DOTALL)
    if titulo:
        aviso_div = '\n<div id="aviso-erro" style="display:none; background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #f5c6cb; font-weight: bold;"></div>\n'
        s = s.replace(titulo.group(1), titulo.group(1) + aviso_div)
        print("OK: Div de aviso adicionada abaixo do titulo.")
    else:
        print("AVISO: Nao achei o titulo da pagina para inserir a div.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

# 2. Ajusta o JavaScript para exibir a div de aviso em vez de tentar usar alert
js_path = "dmpl_functions.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o trecho do catch para mostrar a div de aviso
antigo_catch = '''.catch(error => {
            console.error("Falha na verificacao:", error);
            // Mostra a mensagem de erro na tabela, em vermelho
            if(tbody) {
                tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:#d9534f; font-weight:bold; padding:15px;">⚠️ ${error.message}</td></tr>`;
            }
            // Limpa o grafico
            if (window._chartDMPL) {
                window._chartDMPL.destroy();
                window._chartDMPL = null;
            }
        });'''

novo_catch = '''.catch(error => {
            console.error("Falha na verificacao:", error);
            
            // Esconde o aviso anterior
            const aviso = document.getElementById('aviso-erro');
            if(aviso) {
                aviso.style.display = 'block';
                aviso.innerText = "⚠️ " + error.message;
            } else {
                // Se a div nao existir, cai no alert (fallback)
                alert("Aviso: " + error.message);
            }

            // Limpa a tabela
            if(tbody) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#777;">Nenhum dado para o período.</td></tr>';
            }
            
            // Limpa o grafico
            if (window._chartDMPL) {
                window._chartDMPL.destroy();
                window._chartDMPL = null;
            }
        });'''

# Como o JS foi injetado inline, precisamos atualizar os dois (externo e inline)
js = js.replace(antigo_catch, novo_catch)
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("OK: Arquivo dmpl_functions.js atualizado.")

# Atualiza o script inline no HTML tambem
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui o script inline antigo pelo novo conteudo do JS
padrao_inline = re.compile(r'<script>\s*// VERSAO NOVA DO SCRIPT.*?</script>', re.DOTALL)
novo_inline = f'<script>\n// VERSAO NOVA DO SCRIPT\n{js}\n</script>'

if padrao_inline.search(html):
    html = padrao_inline.sub(novo_inline, html)
    print("OK: Script inline no HTML atualizado.")
else:
    # Se nao achou o comentario, tenta substituir pelo inicio do script
    padrao_inline2 = re.compile(r'<script>\s*(function carregar|console\.log).*?</script>', re.DOTALL)
    if padrao_inline2.search(html):
        html = padrao_inline2.sub(novo_inline, html)
        print("OK: Script inline no HTML atualizado (segunda tentativa).")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("\nPROCESSO CONCLUIDO! Aperte Ctrl+F5 na tela e teste.")
