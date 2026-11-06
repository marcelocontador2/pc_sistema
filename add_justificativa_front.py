import shutil, datetime, ast

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
arq = "pc_frontend/integridade.html"
shutil.copy2(arq, f"{arq}.bak_justificativa_{ts}")

c = open(arq, encoding="utf-8", errors="ignore").read()

# 1. Injetar o Modal e o CSS antes do </body>
modal_html = """
<!-- MODAL DE JUSTIFICATIVA -->
<div id="modalJustificativa" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:#fff; padding:20px; border-radius:8px; width:400px; max-width:90%;">
        <h3 id="modalJustTitulo" style="margin-top:0; color:#003366;">Justificar Inconsistência</h3>
        <p id="modalJustLinha" style="font-weight:bold; color:#dc3545;">Linha</p>
        <textarea id="modalJustTexto" rows="4" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; margin-bottom:15px;" placeholder="Digite a justificativa para esta diferença..."></textarea>
        <div style="display:flex; justify-content:flex-end; gap:10px;">
            <button onclick="fecharModalJust()" style="padding:8px 15px; background:#ccc; border:none; border-radius:4px; cursor:pointer;">Cancelar</button>
            <button onclick="salvarJustificativa()" style="padding:8px 15px; background:#003366; color:white; border:none; border-radius:4px; cursor:pointer;">Salvar Justificativa</button>
        </div>
    </div>
</div>

<script>
// Objeto global para armazenar as justificativas
window.justificativasSalvas = {};
window.linhaAtualJustificativa = "";

function abrirModalJust(linha, elemento) {
    window.linhaAtualJustificativa = linha;
    document.getElementById('modalJustLinha').innerText = "Item: " + linha;
    document.getElementById('modalJustTexto').value = window.justificativasSalvas[linha] || "";
    document.getElementById('modalJustificativa').style.display = 'flex';
}

function fecharModalJust() {
    document.getElementById('modalJustificativa').style.display = 'none';
}

function salvarJustificativa() {
    let texto = document.getElementById('modalJustTexto').value;
    window.justificativasSalvas[window.linhaAtualJustificativa] = texto;
    
    // Opcional: atualizar visual do botão que foi clicado para indicar que foi justificado
    let linha = window.linhaAtualJustificativa;
    let botoes = document.querySelectorAll('.btn-justificar');
    botoes.forEach(btn => {
        if (btn.getAttribute('data-linha') === linha && texto.trim() !== "") {
            btn.style.backgroundColor = "#28a745"; // Fica verde se justificado
            btn.title = "Justificado: " + texto;
        }
    });

    fecharModalJust();
}
</script>
"""

if "<!-- MODAL DE JUSTIFICATIVA -->" not in c:
    c = c.replace("</body>", modal_html + "\n</body>")

# 2. Substituir a função que gera os alertas vermelhos (os números entre parênteses)
# Padrao atual: <td class="...">(1)</td> ou algo similar.
# Vamos buscar o trecho onde os erros (1), (2), etc. são montados.

# Procura o momento onde ele adiciona o texto do erro
# Como não sabemos o código exato, vamos procurar a string "(1)" ou "(2)" e ver como renderiza.
# Mas o ideal é interceptarmos a criação de qualquer tag que contenha o erro numérico.

print("[INFO] Modal e JS injetados no HTML.")
open(arq, "w", encoding="utf-8").write(c)
print("[OK] Backup feito e arquivo salvo.")
