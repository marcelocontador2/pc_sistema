import re

c = open('index.html', encoding='utf-8-sig').read()

# Verifica se o item já existe
if "Comparativo de Despesas" not in c:
    # Localiza o último bloco <script> que contém a adição do Comparativo de Receitas
    # e insere a adição do Despesas logo após o fechamento do bloco
    padrao = r'(<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{\s*setTimeout\(function\(\) \{\s*const submenuAnalises = document\.getElementById\(\'submenu-analises\'\);\s*if \(submenuAnalises\) \{\s*if \(!submenuAnalises\.textContent\.includes\(\'Comparativo de Receitas\'\)\) \{.*?\}\s*\}\s*\}, \d+\);\s*\}\);\s*</script>)'
    
    match = re.search(padrao, c, re.DOTALL)
    if match:
        bloco_antigo = match.group(1)
        bloco_novo = bloco_antigo + """
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
    }, 3000);
});
</script>
"""
        c = c.replace(bloco_antigo, bloco_novo)
        print("[OK] Script de Despesas inserido após o de Receitas!")
    else:
        print("[AVISO] Bloco do script de Receitas não encontrado. Tentando inserir no final do body...")
        # Fallback: insere antes de </body>
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
    }, 3000);
});
</script>
</body>
"""
        c = c.replace("</body>", novo_script)
        print("[OK] Script de Despesas inserido no final do body.")
    
    open('index.html', 'w', encoding='utf-8').write(c)
    print("[OK] index.html atualizado!")
else:
    print("[AVISO] O item 'Comparativo de Despesas' já existe no menu.")
