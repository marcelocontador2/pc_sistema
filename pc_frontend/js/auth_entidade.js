(function () {
    function obterContextoUsuario() {
        let usuarioId = null;
        let entidadeId = null;
        let entidadeNome = '';
        let perfil = '';
        try {
            const raw = localStorage.getItem('usuario_logado');
            if (raw) {
                const u = JSON.parse(raw);
                if (u && u.id != null) usuarioId = String(u.id);
                if (u && u.entidade_id != null && String(u.entidade_id) !== '') {
                    entidadeId = String(u.entidade_id);
                }
                if (u && (u.entidade_nome || u.nome_entidade || u.entidade)) {
                    entidadeNome = String(u.entidade_nome || u.nome_entidade || u.entidade);
                }
                const candPerfil = (u && (u.perfil ?? u.role ?? u.tipo_usuario ?? u.nivel ?? '')) || '';
                perfil = String(candPerfil).trim().toLowerCase();
            }
        } catch (e) {}

        if (!entidadeId) {
            try {
                const sel = localStorage.getItem('entidade_id_selecionada');
                if (sel && String(sel).trim() !== '') entidadeId = String(sel).trim();
            } catch (e) {}
        }
        if (!entidadeNome) {
            try {
                const selNome = localStorage.getItem('entidade_nome_selecionada');
                if (selNome && String(selNome).trim() !== '') entidadeNome = String(selNome).trim();
            } catch (e) {}
        }
        const isAdmin = perfil === 'adm' || perfil === 'admin' || perfil === 'administrador';
        return { usuarioId, entidadeId, entidadeNome, perfil, isAdmin };
    }

    const originalFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
        const opts = Object.assign({}, init || {});
        const headers = new Headers(opts.headers || {});
        const ctx = obterContextoUsuario();
        if (ctx.usuarioId && !headers.has('X-Usuario-Id')) {
            headers.set('X-Usuario-Id', ctx.usuarioId);
        }
        if (ctx.entidadeId && !headers.has('X-Entidade-Id')) {
            headers.set('X-Entidade-Id', ctx.entidadeId);
        }
        opts.headers = headers;
        return originalFetch(input, opts);
    };

    function aplicarMenuEIdentidade() {
        try {
            const params = new URLSearchParams(window.location.search || '');
            if (params.has('sem_poderes')) {
                params.delete('sem_poderes');
                const novaQuery = params.toString();
                const novaUrl = window.location.pathname + (novaQuery ? '?' + novaQuery : '') + window.location.hash;
                if (window.history && window.history.replaceState) {
                    window.history.replaceState({}, document.title, novaUrl);
                }
            }
            sessionStorage.removeItem('aviso_permissao_pendente');
        } catch (e) {}

        const bannerAntigo = document.getElementById('banner-aviso-permissao');
        if (bannerAntigo) bannerAntigo.remove();

        const ctx = obterContextoUsuario();

        if (!ctx.isAdmin) {
            document.querySelectorAll('a, button, li, div, span').forEach((el) => {
                if (el.children && el.children.length > 2) return;
                const href = (el.getAttribute && el.getAttribute('href') || '').toLowerCase();
                const onclick = (el.getAttribute && el.getAttribute('onclick') || '').toLowerCase();
                const texto = (el.textContent || '').trim().toLowerCase();
                const ehItemConfig = href.includes('/configuracoes')
                    || onclick.includes('configuracoes')
                    || texto === 'configuracoes'
                    || texto === 'configura??es';
                if (ehItemConfig) {
                    const alvo = el.closest('li') || el.closest('.menu-item') || el.closest('.nav-item') || el;
                    alvo.style.setProperty('display', 'none', 'important');
                }
            });
        }

        if (ctx.entidadeId && ctx.entidadeId !== '24') {
            document.querySelectorAll('.logo-area img').forEach((img) => {
                img.alt = ctx.entidadeNome || ('Entidade ' + ctx.entidadeId);
                if (!img.dataset.entidadeAjustada) {
                    img.dataset.entidadeAjustada = '1';
                    img.src = '/static/logo-entidade-' + ctx.entidadeId + '.png';
                    img.onerror = function () {
                        if (ctx.entidadeNome) {
                            const span = document.createElement('div');
                            span.style.cssText = 'font-weight:800;font-size:16px;color:#0072BA;line-height:1.2;';
                            span.textContent = ctx.entidadeNome;
                            img.replaceWith(span);
                        } else {
                            img.style.display = 'none';
                        }
                    };
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', aplicarMenuEIdentidade);
    } else {
        aplicarMenuEIdentidade();
    }
    setTimeout(aplicarMenuEIdentidade, 150);
    setTimeout(aplicarMenuEIdentidade, 500);
})();
