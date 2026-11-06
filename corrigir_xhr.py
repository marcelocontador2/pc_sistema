import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/index.html"
shutil.copy2(arq, f"{arq}.bak_upload_xhr_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# Localiza a funcao enviarArquivo (do "async function enviarArquivo" ate o fechamento)
idx = c.find("async function enviarArquivo(event) {")
if idx == -1:
    idx = c.find("function enviarArquivo(event) {")

if idx == -1:
    print("[ERRO] Funcao enviarArquivo nao encontrada.")
else:
    # Encontra o fechamento da funcao (proximo "function" ou "}" no nivel correto)
    # Como a funcao e grande, vamos pegar ate o proximo "function" ou "</script>"
    proximo = c.find("\nfunction ", idx + 10)
    if proximo == -1:
        proximo = c.find("\n</script>", idx + 10)
    if proximo == -1:
        proximo = idx + 5000  # fallback

    # Nova funcao (versao simples, sem async/await, com XMLHttpRequest)
    nova_funcao = '''
function enviarArquivo(event) {
    event.preventDefault();
    
    var tipo = document.getElementById('upload-tipo').value;
    var arquivoInput = document.getElementById('upload-arquivo');
    var ano = document.getElementById('upload-ano').value;
    var mes = document.getElementById('upload-mes').value;
    var trimestre = document.getElementById('upload-trimestre').value;
    var exercicio = document.getElementById('upload-exercicio').value;
    var msgDiv = document.getElementById('msg-upload');
    
    var periodo_tipo = "";
    var periodo_valor = "";
    if (mes) { periodo_tipo = "MES"; periodo_valor = mes; }
    else if (trimestre) { periodo_tipo = "TRIMESTRE"; periodo_valor = trimestre; }
    else if (exercicio) { periodo_tipo = "ANO"; periodo_valor = ano; }
    else {
        msgDiv.innerHTML = "<span style='color: red;'>Selecione um dos períodos.</span>";
        return;
    }
    
    if (!arquivoInput.files || !arquivoInput.files[0]) {
        msgDiv.innerHTML = "<span style='color: red;'>Anexe um arquivo CSV.</span>";
        return;
    }
    
    var formData = new FormData();
    formData.append("file", arquivoInput.files[0]);
    formData.append("tipo_relatorio", tipo);
    formData.append("ano", ano);
    formData.append("periodo_tipo", periodo_tipo);
    formData.append("periodo_valor", periodo_valor);
    
    msgDiv.innerHTML = "<span style='color: blue;'>Enviando arquivo... Aguarde.</span>";
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload", true);
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            var result;
            try { result = JSON.parse(xhr.responseText); } catch(e) { result = {}; }
            msgDiv.innerHTML = "<div style='background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-top: 15px;'><strong>✅ Importação realizada com sucesso!</strong><br>Arquivo: " + (result.arquivo || arquivoInput.files[0].name) + "</div>";
            document.getElementById('form-upload').reset();
        } else {
            msgDiv.innerHTML = "<div style='background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-top: 15px;'><strong>❌ Erro na importação</strong><br>Status: " + xhr.status + "<br>Detalhe: " + xhr.responseText + "</div>";
        }
    };
    
    xhr.onerror = function() {
        msgDiv.innerHTML = "<span style='color: red;'>Erro de conexão com o servidor.</span>";
    };
    
    xhr.send(formData);
}
'''
    
    c = c[:idx] + nova_funcao + c[proximo:]
    open(arq, "w", encoding="utf-8").write(c)
    print("[OK] Funcao enviarArquivo substituida por versao com XMLHttpRequest (mais segura).")
