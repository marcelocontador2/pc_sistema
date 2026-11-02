
// Script para ajustar os textos dos links após o menu ser gerado
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const links = document.querySelectorAll('.submenu a');
        links.forEach(link => {
            // Adiciona sufixos
            if (link.textContent.trim() === 'Análise Orçamentária') {
                link.textContent = 'Análise Orçamentária (BO)';
            }
            if (link.textContent.trim() === 'Análise Patrimonial') {
                link.textContent = 'Análise Patrimonial (DVP)';
            }
            // Troca o hífen por parênteses na Financeira
            if (link.textContent.trim() === 'Análise Financeira-BF') {
                link.textContent = 'Análise Financeira (BF)';
            }
        });
    }, 500);
});
