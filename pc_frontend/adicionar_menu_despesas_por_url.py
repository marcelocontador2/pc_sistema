c = open('index.html', encoding='utf-8-sig').read()

# Verifica se o link do menu já existe pela URL
if 'href="/analise_comparativo_despesas"' not in c:
    novo_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            // Verifica se o link já existe pelo href
            if (!submenuAnalises.querySelector('a[href="/analise_comparativo_despesas"]')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_comparativo_despesas';
                a.textContent = 'Comparativo de Despesas';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 3000);
});
</script>
</body>
"""
    c = c.replace("</body>", novo_script)
    open('index.html', 'w', encoding='utf-8').write(c)
    print("[OK] Link 'Comparativo de Despesas' adicionado ao menu!")
else:
    print("[AVISO] O link já existe no menu.")
