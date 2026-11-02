c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Encontra o trecho onde a mensagem é exibida
trecho_antigo = '''msgDiv.innerHTML = "<div style='background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-top: 15px;'><strong>✅ Upload realizado com sucesso!</strong><br><strong>Arquivo:</strong> " + (result.arquivo || arquivo.name) + "<br><strong>Tipo:</strong> " + (tipo || "Não informado") + "<br><strong>Detalhe:</strong> " + (result.mensagem || "Processado com sucesso.") + "</div>";'''

# Novo sistema de notificação persistente com botão de fechar
trecho_novo = '''
// Exibe a notificação de sucesso persistente
const msgDiv = document.getElementById('msg-upload');
if (msgDiv) {
    msgDiv.innerHTML = `
        <div style="background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>✅ Importação realizada com sucesso!</strong><br>
                <strong>Arquivo:</strong> ${result.arquivo || arquivo.name}<br>
                <strong>Tipo:</strong> ${tipo || "Não informado"}<br>
                <strong>Detalhe:</strong> ${result.mensagem || "Processado com sucesso."}
            </div>
            <button onclick="this.parentElement.style.display='none'" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #155724; font-weight: bold;">&times;</button>
        </div>
    `;
    msgDiv.style.display = 'block';
}'''

# Também precisamos garantir que o erro (vermelho) seja persistente
trecho_antigo_erro = '''msgDiv.innerHTML = "<span style='color: red;'>Erro no servidor: " + (result.detail || "Falha desconhecida") + "</span>";'''
trecho_novo_erro = '''
msgDiv.innerHTML = `
    <div style="background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong>❌ Erro na importação</strong><br>
            <strong>Detalhe:</strong> ${result.detail || "Falha desconhecida"}
        </div>
        <button onclick="this.parentElement.style.display='none'" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #721c24; font-weight: bold;">&times;</button>
    </div>
`;'''

# Aplica as substituições
if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Mensagem de sucesso persistente inserida!")
else:
    print("[AVISO] Trecho de sucesso antigo não encontrado.")

if trecho_antigo_erro in c:
    c = c.replace(trecho_antigo_erro, trecho_novo_erro)
    print("[OK] Mensagem de erro persistente inserida!")
else:
    print("[AVISO] Trecho de erro antigo não encontrado.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado com notificações persistentes!")
