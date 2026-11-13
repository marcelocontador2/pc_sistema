c = open('relatorio_final.html', encoding='utf-8-sig').read()

script_ajuste = """
    <script>
        // Ajusta os gráficos para impressão
        window.addEventListener('beforeprint', function() {
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach(canvas => {
                canvas.style.maxHeight = '250px';
                canvas.style.width = '100%';
            });
        });
        window.addEventListener('afterprint', function() {
            // Restaura o tamanho original (se necessário)
        });
    </script>
"""

if 'beforeprint' not in c:
    c = c.replace('</body>', script_ajuste + '\n</body>')

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] Script de ajuste de gráficos para impressão adicionado!")
