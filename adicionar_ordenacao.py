import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

for arq in ["pc_frontend/index.html", "pc_frontend/normas.html"]:
    try:
        c = open(arq, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue

    c_orig = c

    # Procura o script que constroi o menu (o que tem "const novoLi")
    idx = c.find("const novoLi = document.createElement('li')")
    if idx == -1:
        print(f"[AVISO] {arq} - Nao encontrei o script de construcao do menu.")
        continue

    # Encontra o final do script (proximo </script>)
    fim_script = c.find("</script>", idx)
    if fim_script == -1:
        print(f"[AVISO] {arq} - Nao encontrei o </script>.")
        continue

    # 3. Adiciona uma funcao de ordenacao logo apos o script de construcao
    ordem_js = '''
    // === ORDENACAO DO SUBMENU DE ANALISES ===
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() {
            var submenu = document.getElementById('submenu-analises');
            if (!submenu) return;
            
            // Ordem desejada
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
            
            // Pega todos os <li> do submenu
            var itens = Array.from(submenu.querySelectorAll('li'));
            
            // Cria um mapa de texto -> item
            var mapa = {};
            itens.forEach(function(li) {
                var texto = li.textContent.trim();
                mapa[texto] = li;
            });
            
            // Limpa o submenu
            submenu.innerHTML = '';
            
            // Reinsere na ordem correta
            ordem.forEach(function(texto) {
                if (mapa[texto]) {
                    submenu.appendChild(mapa[texto]);
                }
            });
            
            // Adiciona os itens que nao estao na ordem (se houver)
            itens.forEach(function(li) {
                var texto = li.textContent.trim();
                if (ordem.indexOf(texto) === -1) {
                    submenu.appendChild(li);
                }
            });
        }, 2000); // Espera o menu ser construido
    });
    </script>'''

    c = c[:fim_script] + ordem_js + c[fim_script + 9:]
    shutil.copy2(arq, f"{arq}.bak_ordem_js_{ts}")
    open(arq, "w", encoding="utf-8").write(c)
    print(f"[OK] {arq} - Funcao de ordenacao adicionada (sem tocar no HTML).")

print("\n[OK] Processo concluido. Aperte Ctrl+Shift+R no navegador.")
