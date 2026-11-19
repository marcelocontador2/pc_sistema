import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Remove QUALQUER atributo 'disabled' ou 'pointer-events: none' do HTML
texto = re.sub(r'\bdisabled\b', '', texto)
texto = re.sub(r'pointer-events\s*:\s*none', 'pointer-events: auto', texto)
texto = re.sub(r'opacity\s*:\s*0\.5', 'opacity: 1', texto)
texto = re.sub(r'opacity\s*:\s*0\.6', 'opacity: 1', texto)

# 2. Torna os botoes clicaveis via CSS forcado
style_forcado = '''
<style>
    button { cursor: pointer !important; }
    button:disabled { opacity: 1 !important; cursor: pointer !important; pointer-events: auto !important; }
    .btn:disabled { opacity: 1 !important; cursor: pointer !important; pointer-events: auto !important; }
</style>
'''
if "<style>" not in texto:
    texto = texto.replace("</head>", style_forcado + "</head>")
else:
    texto = texto.replace("</style>", "</style>" + style_forcado, 1)

# 3. Reinjeta o JavaScript de acao nos botoes (usando onclick inline)
js_acao = '''
<script>
// Funcao para exibir alerta se a funcionalidade nao estiver implementada
function aviso(msg) {
    alert(msg);
}

// Reatribui os cliques dos botoes principais
document.addEventListener("DOMContentLoaded", function() {
    // Botao Verificar Dados
    var btnVerificar = document.getElementById("btn-verificar");
    if (btnVerificar) {
        btnVerificar.onclick = function() {
            var ano = document.getElementById("ano").value;
            var tipo = document.getElementById("tipo").value;
            var periodo = document.getElementById("periodo").value;
            var url = "/api/relatorio_consolidado/" + ano + "-" + tipo.toUpperCase() + "-" + periodo;
            fetch(url).then(r => r.json()).then(data => {
                alert("Status: " + data.status + "\\nEncontrados: " + data.total_encontrados + "\\nFaltando: " + data.total_faltando);
            }).catch(e => alert("Erro: " + e));
        };
    }

    // Botao Confirmar e Salvar
    var btnSalvar = document.getElementById("btn-salvar");
    if (btnSalvar) {
        btnSalvar.onclick = function() {
            var ano = document.getElementById("ano").value;
            var tipo = document.getElementById("tipo").value;
            var periodo = document.getElementById("periodo").value;
            var url = "/salvar_relatorio_consolidado/" + ano + "-" + tipo.toUpperCase() + "-" + periodo;
            fetch(url, {method: "POST"}).then(r => r.json()).then(data => {
                if (data.ok) {
                    alert("Relatorio salvo com sucesso!");
                    location.reload();
                } else {
                    alert("Erro ao salvar: " + (data.mensagem || "desconhecido"));
                }
            }).catch(e => alert("Erro: " + e));
        };
    }

    // Botao Gerar PDF
    var btnGerarPdf = document.getElementById("btn-gerar-pdf");
    if (btnGerarPdf) {
        btnGerarPdf.onclick = function() {
            var checkbox = document.querySelector("#lista-historico input[type=checkbox]:checked");
            if (!checkbox) {
                alert("Selecione um historico na lista lateral primeiro.");
                return;
            }
            window.open("/gerar_pdf_relatorio_consolidado/" + checkbox.value, "_blank");
        };
    }

    // Forca todos os botoes a ficarem ativos
    var todosBotoes = document.querySelectorAll("button");
    for (var i = 0; i < todosBotoes.length; i++) {
        todosBotoes[i].disabled = false;
        todosBotoes[i].style.opacity = "1";
        todosBotoes[i].style.pointerEvents = "auto";
    }
});
</script>
'''

# Remove scripts antigos que tentavam desbloquear (para nao conflitar)
texto = re.sub(r'<script>\s*window\.addEventListener\("load".*?</script>', '', texto, flags=re.DOTALL)
texto = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded".*?</script>', '', texto, flags=re.DOTALL)

# Insere o novo script antes do </body>
pos = texto.rfind("</body>")
if pos != -1:
    texto = texto[:pos] + js_acao + texto[pos:]
    print("[OK] Script de acao e desbloqueio injetado.")
else:
    print("[ERRO] Nao encontrei </body>.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo HTML atualizado.")
