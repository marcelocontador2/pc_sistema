
document.addEventListener("DOMContentLoaded", function() {
    // 1. Encontra a lista principal do menu
    const menuPrincipal = Array.from(document.querySelectorAll('ul')).find(ul => ul.textContent.includes('Importar Relatórios'));
    if (!menuPrincipal) return;
    // 2. Cria o novo item "Análises Contábeis" e seu submenu
    const novoLi = document.createElement('li');
    const linkPai = document.createElement('a');
    linkPai.href = '#';
    linkPai.textContent = 'Análises Contábeis';
    linkPai.style.cssText = 'display:block; padding:10px 0px; text-decoration:none; color:#333; font-weight:bold; cursor:pointer;';
    const submenu = document.createElement('ul');
    submenu.className = 'submenu';
    submenu.id = 'submenu-analises';
    submenu.style.cssText = 'list-style: none; padding-left: 0; margin-left: 0; display: none;';
    linkPai.addEventListener('click', function(e) {
        e.preventDefault();
        submenu.classList.toggle('open');
        submenu.style.display = (submenu.style.display === 'none' || submenu.style.display === '') ? 'block' : 'none';
    });
    novoLi.appendChild(linkPai);
    novoLi.appendChild(submenu);
    // 3. Insere o novo item após "Demonstrações Contábeis"
    const liDemonstracoes = Array.from(menuPrincipal.querySelectorAll('li')).find(li => li.textContent.includes('Demonstrações Contábeis'));
    if (liDemonstracoes) {
        liDemonstracoes.parentElement.insertBefore(novoLi, liDemonstracoes.nextSibling);
    } else {
        menuPrincipal.appendChild(novoLi);
    }
    // 4. Move os links de análise para dentro do novo submenu
    const linksParaMover = [
        'Conferência das Demonstrações',
        'Integridade entre Demonstrações',
        'Análise Orçamentária',
        'Análise Financeira-BF',
        'Análise Patrimonial',
        'Composição Receitas/Despesas',
        'Índices de Liquidez',
        'Resultados Gerais'
    ];
    const todosLinks = Array.from(menuPrincipal.querySelectorAll('a'));
    todosLinks.forEach(link => {
        const texto = link.textContent.trim();
        if (linksParaMover.includes(texto)) {
            const novoSubLi = document.createElement('li');
            const novoLink = link.cloneNode(true);
            novoLink.style.cssText = 'display:block; padding:8px 20px 8px 40px; text-decoration:none; color:#666; font-weight:400; font-size:13px;';
            novoSubLi.appendChild(novoLink);
            submenu.appendChild(novoSubLi);
            link.parentElement.remove();
        }
    });
});
