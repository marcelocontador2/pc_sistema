
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        // Encontra o submenu de Análises Contábeis
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            // Verifica se o item já existe para não duplicar
            if (!submenuAnalises.textContent.includes('Custo de Pessoal')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_custo_pessoal';
                a.textContent = 'Custo de Pessoal';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 1000); // Espera o menu ser gerado
});
