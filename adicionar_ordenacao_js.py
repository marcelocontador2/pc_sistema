import shutil, datetime, re

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # Remove qualquer script de ordenacao antigo (para nao duplicar)
    c = re.sub(r'<!-- ORDENACAO SUBMENU ANALISES -->.*?<!-- FIM ORDENACAO -->', '', c, flags=re.DOTALL)

    # Procura o </body> para inserir o script antes
    idx_body = c.rfind("</body>")
    if idx_body == -1:
        print(f"[AVISO] {arq} - Nao encontrei </body>.")
        continue

    script_ordenacao = '''
<!-- ORDENACAO SUBMENU ANALISES -->
<script>
document.addEventListener("DOMContentLoaded", function() {
    // Espera o menu ser montado (3 segundos para garantir)
    setTimeout(function() {
        var submenu = document.getElementById('submenu-analises');
        if (!submenu) {
            console.log("[ORDENACAO] Submenu nao encontrado.");
            return;
        }
        
        var ordem = [
            'Conferência das Demonstrações',
            'Integridade entre Demonstrações',
            'Análise BP',
            'Análise Orçamentária (BO)',
            'Análise Financeira (BF)',
            'Análise DFC',
            'Análise Patrimonial (DVP)',
            'Índices de Liquidez',
            'Composição Receitas/Despesas',
            'Resultados Gerais',
            'Comparativo de Receitas',
            'Comparativo de Despesas',
            'Análise por Centro de Custos',
            'Custo de Pessoal'
        ];
        
        var itens = Array.from(submenu.querySelectorAll('li'));
        var mapa = {};
        itens.forEach(function(li) {
            var texto = li.textContent.trim();
            mapa[texto] = li;
        });
        
        // Limpa e reorganiza
        submenu.innerHTML = '';
        ordem.forEach(function(texto) {
            if (mapa[texto]) {
                submenu.appendChild(mapa[texto]);
            }
        });
        // Adiciona os que nao estao na ordem (se houver)
        itens.forEach(function(li) {
            var texto = li.textContent.trim();
            if (ordem.indexOf(texto) === -1) {
                submenu.appendChild(li);
            }
        });
        
        console.log("[ORDENACAO] Submenu reorganizado.");
    }, 3000);
});
</script>
<!-- FIM ORDENACAO -->
'''

    c = c[:idx_body] + script_ordenacao + c[idx_body:]
    print(f"[OK] {arq} - Script de ordenacao inserido.")

    if c != c_orig:
        shutil.copy2(arq, f"{arq}.bak_ordenacao_{ts}")
        open(arq, "w", encoding="utf-8").write(c)
        print(f"[OK] {arq} - Alteracoes salvas.")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
