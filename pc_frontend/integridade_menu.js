
document.addEventListener("DOMContentLoaded", function() {
    // Procura o menu principal
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;

    // Cria o link 1
    const li1 = document.createElement('li');
    const a1 = document.createElement('a');
    a1.href = "#";
    a1.innerText = "Conferência das Demonstrações";
    a1.style.cursor = "pointer";
    a1.onclick = function(e) {
        e.preventDefault();
        abrirTelaSistema('/conferencia', 'Conferência das Demonstrações');
    };
    li1.appendChild(a1);
    navMenu.appendChild(li1);

    // Cria o link 2
    const li2 = document.createElement('li');
    const a2 = document.createElement('a');
    a2.href = "#";
    a2.innerText = "Integridade entre Demonstrações";
    a2.style.cursor = "pointer";
    a2.onclick = function(e) {
        e.preventDefault();
        abrirTelaSistema('/integridade', 'Integridade entre Demonstrações');
    };
    li2.appendChild(a2);
    navMenu.appendChild(li2);
});

function abrirTelaSistema(url, titulo) {
    // Cria o overlay se não existir
    let overlay = document.getElementById('overlay-sistema');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'overlay-sistema';
        overlay.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:#f4f6f9; z-index:9999; display:none; box-sizing:border-box;';
        
        let conteudo = '<div style="padding:10px 20px; background:#fff; border-bottom:1px solid #ddd; display:flex; align-items:center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">';
        conteudo += '<button onclick="document.getElementById(\'overlay-sistema\').style.display=\'none\'" style="background:#fff; border:1px solid #ccc; padding:8px 15px; border-radius:6px; cursor:pointer; font-weight:bold; color: #333;">&larr; Voltar ao Sistema</button>';
        conteudo += '<h3 id="titulo-overlay-sistema" style="margin-left: 20px; margin-top: 0; margin-bottom: 0; color: #333;">' + titulo + '</h3>';
        conteudo += '</div>';
        conteudo += '<iframe id="iframe-sistema" src="" style="width:100%; height:calc(100% - 50px); border:none;"></iframe>';
        
        overlay.innerHTML = conteudo;
        document.body.appendChild(overlay);
    }
    
    document.getElementById('titulo-overlay-sistema').innerText = titulo;
    document.getElementById('iframe-sistema').src = url;
    overlay.style.display = 'block';
}
