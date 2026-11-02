c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Verifica se o item já existe para não duplicar
if "Análise por Centro de Custos" not in c:
    novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            // Verifica se o item já existe para não duplicar
            if (!submenuAnalises.textContent.includes('Análise por Centro de Custos')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_centro_custos';
                a.textContent = 'Análise por Centro de Custos';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 1500); // Espera um pouco mais que o script anterior (1000ms) para garantir a ordem
});
</script>
</body>
</html>
"""
    # Substitui o fechamento do body/html pelo novo bloco
    c = c.replace("</body>\n</html>", novo_script)
    # Se a quebra de linha for diferente, tenta com \r\n
    if "</body>\n</html>" not in c:
        c = c.replace("</body>\r\n</html>", novo_script)
    
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Link 'Análise por Centro de Custos' adicionado ao menu!")
else:
    print("[AVISO] O link já existe no menu.")
