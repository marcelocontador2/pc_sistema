c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Remove o trecho solto que está quebrando o JavaScript
trecho_solto = """            document.getElementById('form-upload').reset();
            // Exibe a mensagem de confirmação
            const msgDivConfirmacao = document.getElementById('msg-confirmacao-upload');
            msgDivConfirmacao.style.display = 'block';
            msgDivConfirmacao.style.backgroundColor = '#d4edda';
            msgDivConfirmacao.style.color = '#155724';
            msgDivConfirmacao.style.border = '1px solid #c3e6cb';
            msgDivConfirmacao.innerHTML = '<strong>✅ Upload realizado com sucesso!</strong><br>Arquivo: ' + (result.arquivo || arquivo.name) + '<br>Tipo: ' + (tipo || 'Não informado');
            
            // Oculta após 5 segundos
            setTimeout(function() {
                msgDivConfirmacao.style.display = 'none';
            }, 5000);"""

if trecho_solto in c:
    c = c.replace(trecho_solto, "")
    print("[OK] Trecho solto removido!")
else:
    # Tenta remover de forma mais flexível
    import re
    c = re.sub(r'document\.getElementById\(\'form-upload\'\)\.reset\(\);\s*// Exibe a mensagem de confirmação.*?setTimeout\(function\(\) \{\s*msgDivConfirmacao\.style\.display = \'none\';\s*\}, 5000\);', '', c, flags=re.DOTALL)
    print("[OK] Trecho solto removido via regex!")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html corrigido!")
