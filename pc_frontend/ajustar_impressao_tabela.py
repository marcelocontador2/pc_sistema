c = open('relatorio_final.html', encoding='utf-8-sig').read()

# Ajusta a função prepararImpressao para remover max-height das tabelas
if 'function prepararImpressao' in c:
    # Remove a função antiga
    import re
    c = re.sub(r'function prepararImpressao\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)

nova_funcao = """
        function prepararImpressao() {
            // Remove imagens antigas
            document.querySelectorAll('.canvas-img').forEach(img => img.remove());
            
            // Converte cada canvas em imagem
            const canvases = document.querySelectorAll('canvas');
            canvases.forEach(canvas => {
                try {
                    const img = document.createElement('img');
                    img.src = canvas.toDataURL('image/png');
                    img.className = 'canvas-img';
                    img.style.cssText = 'display: none; max-width: 100%; max-height: 220px; margin: 0 auto;';
                    canvas.parentNode.insertBefore(img, canvas.nextSibling);
                } catch (e) {
                    console.error('Erro ao converter canvas:', e);
                }
            });
            
            // Remove restrições de altura das tabelas para não cortar
            document.querySelectorAll('.table-container').forEach(el => {
                el.style.maxHeight = 'none';
                el.style.overflow = 'visible';
            });
            
            // Ativa a impressão
            setTimeout(() => {
                document.querySelectorAll('.canvas-img').forEach(img => {
                    img.style.display = 'block';
                });
                window.print();
                
                // Restaura após impressão
                setTimeout(() => {
                    document.querySelectorAll('.canvas-img').forEach(img => img.remove());
                    document.querySelectorAll('canvas').forEach(c => c.style.display = 'block');
                }, 1000);
            }, 200);
        }
"""

pos = c.rfind('</script>')
if pos != -1:
    c = c[:pos] + nova_funcao + "\n" + c[pos:]

open('relatorio_final.html', 'w', encoding='utf-8').write(c)
print("[OK] Função de impressão ajustada para não cortar tabelas!")
