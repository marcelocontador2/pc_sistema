import re

path = "dmpl_functions.js"
with open(path, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o bloco do catch para uma mensagem mais amigavel
antigo_catch = '''.catch(error => {
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

novo_catch = '''.catch(error => {
            console.error("Falha na verificacao:", error);
            
            // Monta uma mensagem amigavel
            let mensagemAmigavel = "Não há dados importados para o período " + periodoFormatado + ".";
            if (error.message && error.message.includes("404")) {
                mensagemAmigavel = "Não há dados importados para o período " + periodoFormatado + ". Verifique se o arquivo CSV foi enviado.";
            } else if (error.message) {
                mensagemAmigavel = error.message;
            }

            // Mostra a div de aviso vermelha
            const aviso = document.getElementById('aviso-erro');
            if(aviso) {
                aviso.style.display = 'block';
                aviso.innerHTML = "⚠️ <strong>Aviso:</strong> " + mensagemAmigavel;
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

if antigo_catch in js:
    js = js.replace(antigo_catch, novo_catch)
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK: Mensagem de erro melhorada no arquivo JS.")
else:
    print("AVISO: Trecho do catch nao encontrado. Tentando substituicao manual...")
    # Tenta uma substituicao mais flexivel
    js = re.sub(r'\.catch\(error => \{.*?\}\);', novo_catch, js, flags=re.DOTALL)
    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("OK: Tentativa de substituicao manual concluida.")

# Atualiza o script inline no HTML
path_html = "analise_dmpl.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

# Atualiza o script inline (se existir)
padrao_inline = re.compile(r'<script>\s*// VERSAO NOVA DO SCRIPT.*?</script>', re.DOTALL)
novo_inline = f'<script>\n// VERSAO NOVA DO SCRIPT\n{js}\n</script>'

if padrao_inline.search(html):
    html = padrao_inline.sub(novo_inline, html)
    print("OK: Script inline no HTML atualizado.")
else:
    print("AVISO: Script inline nao encontrado para atualizar.")

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
