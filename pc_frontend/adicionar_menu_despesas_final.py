c = open('index.html', encoding='utf-8-sig').read()

# Verifica se o link já existe
if "Comparativo de Despesas" not in c:
    novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            if (!submenuAnalises.textContent.includes('Comparativo de Despesas')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_comparativo_despesas';
                a.textContent = 'Comparativo de Despesas';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 2500);
});
</script>
</body>
</html>
"""
    c = c.replace("</body>\n</html>", novo_script)
    if "</body>\n</html>" not in c:
        c = c.replace("</body>\r\n</html>", novo_script)
    
    open('index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Link 'Comparativo de Despesas' adicionado ao menu principal!")
else:
    print("[AVISO] O link já existe no menu.")
