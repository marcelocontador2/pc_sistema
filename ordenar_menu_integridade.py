import re, shutil, datetime

arquivo = r"pc_frontend\index.html"
backup = f"pc_frontend\\index_backup_ordem_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Verifica se já existe a função de ordenação (para não duplicar)
if "// --- FORÇAR ORDEM DO SUBMENU ---" not in html:
    script_ordem = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // --- FORÇAR ORDEM DO SUBMENU ---
    // Espera o menu dinâmico ser montado (pequeno delay para garantir)
    setTimeout(function() {
        // Encontra o submenu de Análises Contábeis
        const submenu = document.querySelector('#submenu-analises');
        if (!submenu) return;
        
        // Pega todos os itens <li> do submenu
        const itens = Array.from(submenu.querySelectorAll('li'));
        
        // Função que encontra um item pelo texto
        const acharItem = (texto) => itens.find(li => li.textContent.trim().includes(texto));
        
        // Localiza o item "Integridade entre Demonstrações"
        const itemIntegridade = acharItem('Integridade entre Demonstrações');
        // Localiza o item "Conferência das Demonstrações" (para saber onde inserir)
        const itemConferencia = acharItem('Conferência das Demonstrações');
        
        if (itemIntegridade && itemConferencia) {
            // Move o item "Integridade" para logo APÓS "Conferência"
            // Se o próximo irmão de Conferência não for Integridade, insere
            if (itemConferencia.nextElementSibling !== itemIntegridade) {
                submenu.insertBefore(itemIntegridade, itemConferencia.nextElementSibling);
            }
        }
    }, 200); // Aguarda 200ms para garantir que o JS do menu já rodou
});
</script>
"""
    
    # Insere o script antes do fechamento do </body>
    idx_body = html.find("</body>")
    if idx_body != -1:
        html = html[:idx_body] + script_ordem + html[idx_body:]
        print("[OK] Script de reordenação injetado.")
    else:
        print("[AVISO] Não encontrei </body>.")
else:
    print("[INFO] Script de ordenação já existe no arquivo.")

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== PROXIMO PASSO ===")
print("1. Na tela do menu, aperte Ctrl+Shift+R.")
print("2. O item 'Integridade entre Demonstrações' deve estar logo abaixo de 'Conferência das Demonstrações'.")
