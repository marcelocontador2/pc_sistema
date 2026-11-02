import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Padrão para encontrar a função enviarArquivo inteira
padrao = r'async function enviarArquivo\(event\) \{.*?\n\}'

nova_funcao = '''async function enviarArquivo(event) {
    event.preventDefault();
    
    const tipo = document.getElementById('upload-tipo').value;
    const arquivo = document.getElementById('upload-arquivo').files[0];
    const ano = document.getElementById('upload-ano').value;
    const mes = document.getElementById('upload-mes').value;
    const trimestre = document.getElementById('upload-trimestre').value;
    const exercicio = document.getElementById('upload-exercicio').value;
    const msgDiv = document.getElementById('msg-upload');
    
    let periodo_tipo = "", periodo_valor = "";
    if (mes) { periodo_tipo = "MES"; periodo_valor = mes; }
    else if (trimestre) { periodo_tipo = "TRIMESTRE"; periodo_valor = trimestre; }
    else if (exercicio) { periodo_tipo = "ANO"; periodo_valor = ano; }
    else { msgDiv.innerHTML = "<span style='color: red;'>Selecione um dos períodos.</span>"; return; }
    
    if (!arquivo) { msgDiv.innerHTML = "<span style='color: red;'>Anexe um arquivo CSV.</span>"; return; }
    
    const formData = new FormData();
    formData.append("file", arquivo);
    formData.append("tipo_relatorio", tipo);
    formData.append("ano", ano);
    formData.append("periodo_tipo", periodo_tipo);
    formData.append("periodo_valor", periodo_valor);
    
    msgDiv.innerHTML = "<span style='color: blue;'>Enviando arquivo... Aguarde.</span>";
    
    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        let result;
        try {
            result = await response.json();
        } catch (e) {
            throw new Error("O servidor não retornou um JSON válido.");
        }
        
        if (response.ok) {
            // Exibe a notificação persistente
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
            document.getElementById('form-upload').reset();
            document.getElementById('upload-ano').value = "2026";
            
            // Redireciona para a tela de análise se for Centro de Custos
            if (tipo && tipo.toUpperCase() === "CENTRO_CUSTOS") {
                setTimeout(function() {
                    window.location.href = "/analise_centro_custos";
                }, 1500);
            }
        } else {
            msgDiv.innerHTML = `
                <div style="background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>❌ Erro na importação</strong><br>
                        <strong>Detalhe:</strong> ${result.detail || "Falha desconhecida"}
                    </div>
                    <button onclick="this.parentElement.style.display='none'" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #721c24; font-weight: bold;">&times;</button>
                </div>
            `;
        }
    } catch (error) {
        console.error("Erro no upload:", error);
        msgDiv.innerHTML = "<span style='color: red;'>Erro de conexão: " + error.message + "</span>";
    }
}'''

if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
    print("[OK] Função enviarArquivo reescrita do zero!")
else:
    print("[ERRO] Função enviarArquivo não encontrada no arquivo.")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado!")
