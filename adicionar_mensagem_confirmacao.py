c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Verifica se a mensagem já está sendo exibida
if 'id="msg-confirmacao-upload"' not in c:
    # 1. Adiciona a div da mensagem no formulário de upload
    c = c.replace(
        '<div id="msg-upload"></div>',
        '<div id="msg-upload"></div>\n            <div id="msg-confirmacao-upload" style="display: none; margin-top: 15px; padding: 15px; border-radius: 5px;"></div>'
    )
    
    # 2. Adiciona a lógica de exibição no final da função de upload
    # Encontra o fechamento do bloco if (response.ok)
    marcador = 'document.getElementById(\'form-upload\').reset();'
    
    if marcador in c:
        script_novo = '''document.getElementById('form-upload').reset();
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
            }, 5000);
            '''
        c = c.replace(marcador, script_novo)
        print("[OK] Mensagem de confirmação adicionada ao upload!")
    else:
        print("[AVISO] Marcador de reset não encontrado.")
else:
    print("[AVISO] A mensagem de confirmação já existe.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado com mensagem de confirmação!")
