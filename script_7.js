
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const submenuAnalises = document.getElementById('submenu-analises');
        if (submenuAnalises) {
            // Verifica se o item já existe para não duplicar
            if (!submenuAnalises.textContent.includes('Análise por Centro de Custos')) {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '/analise_centro_custos';
                a.textContent = 'Análise por Centro de Custos';
                a.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold;';
                li.appendChild(a);
                submenuAnalises.appendChild(li);
            }
        }
    }, 1500); // Espera um pouco mais que o script anterior (1000ms) para garantir a ordem
});
