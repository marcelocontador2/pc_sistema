import re, shutil

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_botao_habilitado")

# 1. Remove qualquer atributo disabled do botao Exibir
s = re.sub(r'<button([^>]*)onclick="exibirNovo\(\)"([^>]*)>', r'<button\1onclick="exibirNovo()" style="background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;"\2>', s)

# 2. Adiciona um script no final para habilitar o botao via JS
js_fix = """
<script>
    // Garante que o botao Exibir esteja sempre habilitado e visivel
    document.addEventListener('DOMContentLoaded', function() {
        const botoes = document.querySelectorAll('button');
        botoes.forEach(function(btn) {
            if (btn.textContent.trim() === 'Exibir') {
                btn.disabled = false;
                btn.style.backgroundColor = '#28a745';
                btn.style.color = 'white';
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
            }
        });
    });
</script>
"""

if "Garante que o botao Exibir" not in s:
    s = s.replace('</body>', js_fix + '\n</body>')
    print("OK: Script de habilitacao do botao adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("FRONTEND CORRIGIDO!")
