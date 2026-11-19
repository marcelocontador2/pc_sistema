import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_frontend/relatorio_consolidado.html")
texto = arquivo.read_text(encoding="utf-8")

# 1. Remove o atributo 'disabled' dos botoes principais se eles existirem
texto = texto.replace('id="btn-gerar-pdf" disabled', 'id="btn-gerar-pdf"')
texto = texto.replace('id="btn-salvar" disabled', 'id="btn-salvar"')
texto = texto.replace('id="btn-verificar" disabled', 'id="btn-verificar"')

# 2. Adiciona um script simples no final do HTML para garantir que os botoes de acao funcionem
script_garantia = '''
<script>
// Garante que os botoes principais nunca fiquem travados por falta de JS
document.addEventListener("DOMContentLoaded", function() {
    var botoes = ["btn-gerar-pdf", "btn-salvar", "btn-verificar", "btn-exibir", "btn-excluir"];
    for (var i = 0; i < botoes.length; i++) {
        var el = document.getElementById(botoes[i]);
        if (el) {
            el.disabled = false;
            el.style.opacity = "1";
            el.style.pointerEvents = "auto";
        }
    }
});
</script>
</body>
</html>
'''

# Remove qualquer script antigo de garantia que ja exista
if "// Garante que os botoes principais nunca fiquem travados" in texto:
    inicio = texto.find("<script>\n// Garante que os botoes principais")
    if inicio == -1:
        inicio = texto.find("<script>// Garante que os botoes principais")
    if inicio != -1:
        fim = texto.find("</script>", inicio) + len("</script>")
        texto = texto[:inicio] + texto[fim:]

# Insere o novo script antes do </body>
pos = texto.rfind("</body>")
if pos != -1:
    texto = texto[:pos] + script_garantia + texto[pos:]
    print("[OK] Script de desbloqueio injetado.")
else:
    print("[ERRO] Nao encontrei </body>.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo HTML atualizado.")
