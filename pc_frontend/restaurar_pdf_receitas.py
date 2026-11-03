c = open('analise_comparativo_receitas.html', encoding='utf-8').read()

# 1. Substitui o botão de PDF para chamar a função correta
antigo_btn = '<button class="btn btn-pdf" onclick="window.print()">Gerar PDF</button>'
novo_btn = '<button class="btn btn-pdf" onclick="gerarPDF()">Gerar PDF</button>'
c = c.replace(antigo_btn, novo_btn)

# 2. Injeta a função gerarPDF() no final do bloco <script>
funcao_pdf = """
        function gerarPDF() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo').value;
            const valor = document.getElementById('valor').value;
            const periodo = `${ano}-${tipo}-${valor}`;
            
            // Chama a rota original de geração de relatório passando o período
            window.open(`/gerar_pdf_comparativo_receitas?periodo_atual=${periodo}`, '_blank');
        }
        
        document.addEventListener('DOMContentLoaded', () => {"""

# Insere a função antes do addEventListener final
c = c.replace("        document.addEventListener('DOMContentLoaded', () => {", funcao_pdf)

open('analise_comparativo_receitas.html', 'w', encoding='utf-8').write(c)
print("[OK] Botão 'Gerar PDF' reconectado à sua rota original!")
