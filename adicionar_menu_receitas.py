c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

if "Comparativo de Receitas" not in c:
    novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            if (!submenuAnalises.textContent.includes('Comparativo de Receitas')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_comparativo_receitas';
                a.textContent = 'Comparativo de Receitas';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 2000); // Espera um pouco mais para garantir que o menu anterior já foi criado
});
</script>
</body>
</html>
"""
    c = c.replace("</body>\n</html>", novo_script)
    if "</body>\n</html>" not in c:
        c = c.replace("</body>\r\n</html>", novo_script)
    
    open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Link 'Comparativo de Receitas' adicionado ao menu!")
else:
    print("[AVISO] O link já existe no menu.")
