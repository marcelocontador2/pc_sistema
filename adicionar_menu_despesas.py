c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# 1. Adiciona a opção no dropdown de importação
if "COMPARATIVO_DESPESAS" not in c:
    c = c.replace(
        '<option value="COMPARATIVO_RECEITAS">Comparativo de Receitas</option>',
        '<option value="COMPARATIVO_RECEITAS">Comparativo de Receitas</option>\n            <option value="COMPARATIVO_DESPESAS">Comparativo de Despesas</option>'
    )
    print("[OK] Opção 'Comparativo de Despesas' adicionada ao dropdown!")

# 2. Adiciona o link no menu (se ainda não existir)
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
    print("[OK] Link 'Comparativo de Despesas' adicionado ao menu!")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado!")
