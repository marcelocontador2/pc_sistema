
                async function carregarConfiguracoes(id = null) {
            if (!id) id = localStorage.getItem('entidade_id_selecionada');
            const url = (id && id !== 'null' && id !== 'undefined') ? `/api/configuracoes/entidade?id=${id}` : '/api/configuracoes/entidade';
            
            try {
                const r = await fetch(url);
                const data = await r.json();
                
                // Preenche todos os campos
                for (const [key, value] of Object.entries(data)) {
                    const el = document.getElementById(key);
                    if (el && key !== 'logo_path' && key !== 'id') el.value = value || '';
                }
                
                // Guarda o ID no input hidden
                if (data.id) {
                    document.getElementById('entidade-id').value = data.id;
                }
                
                // Preview do logo
                const preview = document.getElementById('preview-logo');
                if (data.logo_path) {
                    let nomeArq = data.logo_path;
                    if (nomeArq.includes('/') || nomeArq.includes('\\')) {
                        nomeArq = nomeArq.split(/[\\/]/).pop();
                    }
                    preview.innerHTML = '<img src="/static_logos/' + encodeURIComponent(nomeArq) + '" style="max-height: 80px; max-width: 200px;" onerror="this.style.display=\'none\'; this.parentElement.innerHTML=\'<p style=\'color:#888\'>Logo nao encontrada. Envie novamente.</p>\'">';
                } else {
                    preview.innerHTML = '<p style="color: #888;">Nenhuma logo cadastrada.</p>';
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function carregarEntidades() {
            try {
                const r = await fetch('/api/entidades');
                if (!r.ok) throw new Error("HTTP " + r.status);
                const lista = await r.json();
                const select = document.getElementById('select-entidade');
                
                if (lista.length === 0) {
                    select.innerHTML = '<option value="">Nenhuma entidade cadastrada</option>';
                    return;
                }
                
                select.innerHTML = '';
                lista.forEach(ent => {
                    const opt = document.createElement('option');
                    opt.value = ent.id;
                    opt.textContent = (ent.nome_fantasia || ent.razao_social || 'Sem nome') + ' (ID: ' + ent.id + ')';
                    select.appendChild(opt);
                });
                
                // Tenta pegar do localStorage, senao pega a primeira
                let idSalvo = localStorage.getItem('entidade_id_selecionada');
                const idValido = lista.some(e => String(e.id) === String(idSalvo));
                if (!idValido) {
                    idSalvo = String(lista[0].id);
                    localStorage.setItem('entidade_id_selecionada', idSalvo);
                }
                select.value = idSalvo;
                
                // Carrega os dados da entidade selecionada
                await carregarConfiguracoes(idSalvo);
            } catch (e) {
                console.error('Erro ao carregar entidades:', e);
                document.getElementById('select-entidade').innerHTML = '<option value="">Erro ao carregar</option>';
            }
        }
                
                select.innerHTML = '';
                lista.forEach(ent => {
                    const opt = document.createElement('option');
                    opt.value = ent.id;
                    opt.textContent = (ent.nome_fantasia || ent.razao_social || 'Sem nome') + ' (ID: ' + ent.id + ')';
                    select.appendChild(opt);
                });
                
                // Seleciona a entidade salva no localStorage (ou a primeira)
                let idSalvo = localStorage.getItem('entidade_id_selecionada');
                if (!idSalvo || !lista.find(e => String(e.id) === idSalvo)) {
                    idSalvo = String(lista[0].id);
                    localStorage.setItem('entidade_id_selecionada', idSalvo);
                }
                select.value = idSalvo;
                
                // Carrega os dados da entidade selecionada
                await carregarConfiguracoes(idSalvo);
            } catch (e) {
                console.error('Erro ao carregar entidades:', e);
            }
        }

        async function trocarEntidade() {
            const select = document.getElementById('select-entidade');
            const id = select.value;
            if (!id) return;
            
            localStorage.setItem('entidade_id_selecionada', id);
            await carregarConfiguracoes(id);
            
            // Atualiza o titulo
            document.querySelector('h1').textContent = 'Configuracoes - Cadastro da Entidade';
        }

        function novaEntidade() {
            if (!confirm('Criar uma nova entidade? O formulario sera limpo.')) return;
            
            // Limpa todos os campos (exceto logo_path e id)
            const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
            campos.forEach(c => {
                const el = document.getElementById(c);
                if (el) el.value = '';
            });
            
            // Limpa o ID (sera novo)
            document.getElementById('entidade-id').value = '';
            document.querySelector('h1').textContent = 'Configuracoes - Nova Entidade';
            
            // Limpa o select
            document.getElementById('select-entidade').value = '';
        }

        async function excluirEntidade() {
            const id = document.getElementById('entidade-id').value;
            if (!id) {
                alert('Nenhuma entidade selecionada para excluir.');
                return;
            }
            
            const nome = document.getElementById('razao_social').value || 'esta entidade';
            if (!confirm('Tem certeza que deseja EXCLUIR "' + nome + '"? Esta acao nao pode ser desfeita!')) return;
            
            try {
                const r = await fetch('/api/entidades/' + id, { method: 'DELETE' });
                const data = await r.json();
                
                if (data.ok) {
                    alert('Entidade excluida com sucesso!');
                    localStorage.removeItem('entidade_id_selecionada');
                    await carregarEntidades();
                } else {
                    alert('Erro ao excluir: ' + (data.mensagem || 'Erro desconhecido'));
                }
            } catch (e) {
                alert('Erro de conexao: ' + e.message);
            }
        }
                const preview = document.getElementById('preview-logo');
                if (data.logo_path) {
                    // O backend salva so o nome do arquivo (ex: logo_a1b2c3d4.png)
                    let nomeArq = data.logo_path;
                    if (nomeArq.includes('/') || nomeArq.includes('\\')) {
                        nomeArq = nomeArq.split(/[\\/]/).pop();
                    }
                    preview.innerHTML = '<img src="/static_logos/' + encodeURIComponent(nomeArq) + '" style="max-height: 80px; max-width: 200px;" onerror="this.style.display=\'none\'; this.parentElement.innerHTML=\'<p style=\'color:#888\'>Logo nao encontrada. Envie novamente.</p>\'">';
                } else {
                    preview.innerHTML = '<p style="color: #888;">Nenhuma logo cadastrada.</p>';
                }
            }).catch(e => console.error(e));
        }

        function uploadLogo() {
            const input = document.getElementById('input-logo');
            if (!input.files || input.files.length === 0) return;
            const formData = new FormData();
            formData.append('file', input.files[0]);
            fetch('/api/configuracoes/logo', { method: 'POST', body: formData })
            .then(r => r.json()).then(data => {
                if (data.ok) { alert("Logo enviada com sucesso!"); carregarEntidades(); }
                else { alert("Erro: " + (data.mensagem || "Falha no upload.")); }
            }).catch(e => alert("Erro de conexao: " + e.message));
        }

        async function buscarCEP() {
            const cepInput = document.getElementById('cep');
            let cep = cepInput.value.replace(/\D/g, '');
            
            if (cep.length !== 8) return;  // CEP incompleto, nao busca
            
            // Formata o CEP com traco (ex: 70000-000)
            cepInput.value = cep.slice(0, 5) + '-' + cep.slice(5);
            
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                
                if (!data.erro) {
                    document.getElementById('logradouro').value = data.logradouro || '';
                    document.getElementById('bairro').value = data.bairro || '';
                    document.getElementById('cidade').value = data.localidade || '';
                    document.getElementById('uf').value = data.uf || '';
                    // Foca no campo Numero, para o usuario digitar
                    document.getElementById('numero').focus();
                }
            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        }

        function salvarConfiguracoes() {
            const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
            const dados = {};
            const idEntidade = document.getElementById('entidade-id').value;
            if (idEntidade) dados['id'] = parseInt(idEntidade);
            campos.forEach(c => { const el = document.getElementById(c); if (el) dados[c] = el.value; });
            
            const btn = event.target;
            const textoOriginal = btn.innerText;
            btn.innerText = "Salvando...";
            btn.disabled = true;

            fetch('/api/configuracoes/entidade', {
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify(dados)
            })
            .then(r => {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            })
            .then(data => {
                if (data.ok) {
                    // Mostra o alerta verde
                    const msg = document.getElementById('msg-sucesso');
                    msg.style.display = 'block';
                    // Garante que a mensagem fique visivel por pelo menos 4 segundos
                    msg.scrollIntoView({behavior: 'smooth', block: 'center'});
                    setTimeout(() => { msg.style.display = 'none'; }, 4000);
                    // Fallback: mostra alert nativo tambem, para garantir visibilidade
                    alert("Configuracoes salvas com sucesso!");
                    carregarEntidades();
                } else { 
                    alert("Erro: " + (data.mensagem || "Falha ao salvar.")); 
                }
            })
            .catch(e => {
                alert("Erro de conexao: " + e.message);
            })
            .finally(() => {
                btn.innerText = textoOriginal;
                btn.disabled = false;
            });
        }
        document.addEventListener('DOMContentLoaded', carregarEntidades);
    