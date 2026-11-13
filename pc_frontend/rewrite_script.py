import re, shutil

path = "configuracoes.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_rewrite_script")
print(f"OK: backup salvo em {path}.bak_rewrite_script")

# -----------------------------------------------------------------------
# 1) Localiza a posicao do <script> e do </script>
# -----------------------------------------------------------------------
pos_script = s.find('<script>')
pos_fecha = s.find('</script>', pos_script)

if pos_script == -1 or pos_fecha == -1:
    print("ERRO: tag <script> nao encontrada")
    exit(1)

# -----------------------------------------------------------------------
# 2) Reescreve todo o bloco
# -----------------------------------------------------------------------
script_novo = '''<script>
    async function carregarConfiguracoes(id = null) {
        if (!id) id = localStorage.getItem('entidade_id_selecionada');
        const url = (id && id !== 'null' && id !== 'undefined')
            ? '/api/configuracoes/entidade?id=' + id
            : '/api/configuracoes/entidade';

        try {
            const r = await fetch(url);
            const data = await r.json();

            for (const [key, value] of Object.entries(data)) {
                const el = document.getElementById(key);
                if (el && key !== 'logo_path' && key !== 'id') el.value = value || '';
            }

            const hiddenId = document.getElementById('entidade-id');
            if (hiddenId) hiddenId.value = data.id || '';

            const preview = document.getElementById('preview-logo');
            if (data.logo_path) {
                let nomeArq = data.logo_path;
                if (nomeArq.includes('/') || nomeArq.includes('\\\\')) {
                    nomeArq = nomeArq.split(/[\\\\/]/).pop();
                }
                preview.innerHTML = '<img src="/static_logos/' + encodeURIComponent(nomeArq) + '" style="max-height: 80px; max-width: 200px;" onerror="this.style.display=\\'none\\';">';
            } else {
                preview.innerHTML = '<p style="color: #888;">Nenhuma logo cadastrada.</p>';
            }
        } catch (e) {
            console.error('Erro ao carregar configuracoes:', e);
        }
    }

    async function carregarEntidades() {
        try {
            const r = await fetch('/api/entidades');
            if (!r.ok) throw new Error('HTTP ' + r.status);
            const lista = await r.json();
            const select = document.getElementById('select-entidade');

            if (lista.length === 0) {
                select.innerHTML = '<option value="">Nenhuma entidade cadastrada</option>';
                return;
            }

            select.innerHTML = '';
            lista.forEach(function(ent) {
                const opt = document.createElement('option');
                opt.value = ent.id;
                opt.textContent = (ent.nome_fantasia || ent.razao_social || 'Sem nome') + ' (ID: ' + ent.id + ')';
                select.appendChild(opt);
            });

            let idSalvo = localStorage.getItem('entidade_id_selecionada');
            const valido = lista.some(function(e) { return String(e.id) === String(idSalvo); });
            if (!valido) {
                idSalvo = String(lista[0].id);
                localStorage.setItem('entidade_id_selecionada', idSalvo);
            }
            select.value = idSalvo;

            await carregarConfiguracoes(idSalvo);
        } catch (e) {
            console.error('Erro ao carregar entidades:', e);
            document.getElementById('select-entidade').innerHTML = '<option value="">Erro ao carregar</option>';
        }
    }

    async function trocarEntidade() {
        const select = document.getElementById('select-entidade');
        const id = select.value;
        if (!id) return;
        localStorage.setItem('entidade_id_selecionada', id);
        await carregarConfiguracoes(id);
        document.querySelector('h1').textContent = 'Configuracoes - Cadastro da Entidade';
    }

    function novaEntidade() {
        if (!confirm('Criar uma nova entidade? O formulario sera limpo.')) return;
        const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
        campos.forEach(function(c) {
            const el = document.getElementById(c);
            if (el) el.value = '';
        });
        document.getElementById('entidade-id').value = '';
        document.querySelector('h1').textContent = 'Configuracoes - Nova Entidade';
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

    function uploadLogo() {
        const input = document.getElementById('input-logo');
        if (!input.files || input.files.length === 0) return;
        const formData = new FormData();
        formData.append('file', input.files[0]);
        fetch('/api/configuracoes/logo', { method: 'POST', body: formData })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) {
                    alert('Logo enviada com sucesso!');
                    carregarConfiguracoes();
                } else {
                    alert('Erro: ' + (data.mensagem || 'Falha no upload.'));
                }
            })
            .catch(function(e) { alert('Erro de conexao: ' + e.message); });
    }

    async function buscarCEP() {
        const cepInput = document.getElementById('cep');
        let cep = cepInput.value.replace(/\\D/g, '');
        if (cep.length !== 8) return;

        cepInput.value = cep.slice(0, 5) + '-' + cep.slice(5);

        try {
            const response = await fetch('https://viacep.com.br/ws/' + cep + '/json/');
            const data = await response.json();
            if (!data.erro) {
                document.getElementById('logradouro').value = data.logradouro || '';
                document.getElementById('bairro').value = data.bairro || '';
                document.getElementById('cidade').value = data.localidade || '';
                document.getElementById('uf').value = data.uf || '';
                document.getElementById('numero').focus();
            }
        } catch (error) {
            console.error('Erro ao buscar CEP:', error);
        }
    }

    async function salvarConfiguracoes() {
        const campos = ['razao_social', 'nome_fantasia', 'cnpj', 'endereco', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'email', 'telefone', 'contador_nome', 'contador_crc', 'contador_uf', 'contador_cpf', 'contador_email'];
        const dados = {};

        const idEntidade = document.getElementById('entidade-id').value;
        if (idEntidade) dados['id'] = parseInt(idEntidade);

        campos.forEach(function(c) {
            const el = document.getElementById(c);
            if (el) dados[c] = el.value;
        });

        const btn = event.target;
        const textoOriginal = btn.innerText;
        btn.innerText = 'Salvando...';
        btn.disabled = true;

        try {
            const r = await fetch('/api/configuracoes/entidade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(dados)
            });
            if (!r.ok) throw new Error('HTTP ' + r.status);
            const data = await r.json();

            if (data.ok) {
                const msg = document.getElementById('msg-sucesso');
                msg.style.display = 'block';
                msg.scrollIntoView({behavior: 'smooth', block: 'center'});
                setTimeout(function() { msg.style.display = 'none'; }, 4000);
                alert('Configuracoes salvas com sucesso!');
                await carregarEntidades();
            } else {
                alert('Erro: ' + (data.mensagem || 'Falha ao salvar.'));
            }
        } catch (e) {
            alert('Erro de conexao: ' + e.message);
        } finally {
            btn.innerText = textoOriginal;
            btn.disabled = false;
        }
    }

    document.addEventListener('DOMContentLoaded', carregarEntidades);
</script>'''

# Substitui o bloco
s = s[:pos_script] + script_novo + s[pos_fecha + len('</script>'):]

with open(path, "w", encoding="utf-8") as f:
    f.write(s)

print("OK: bloco <script> inteiro reescrito")

# -----------------------------------------------------------------------
# 3) Verificacao final
# -----------------------------------------------------------------------
abre = s.count('{')
fecha = s.count('}')
print("\n=== VERIFICACAO ===")
print("Chaves abertas:", abre)
print("Chaves fechadas:", fecha)
print("Parenteses abre:", s.count('('))
print("Parenteses fecha:", s.count(')'))

if abre == fecha:
    print("OK: chaves balanceadas")
else:
    print("AVISO: ainda ha desequilibrio de chaves")

# Mostra quantas funcoes existem
for fn in ['carregarConfiguracoes', 'carregarEntidades', 'trocarEntidade', 'novaEntidade', 'excluirEntidade', 'uploadLogo', 'buscarCEP', 'salvarConfiguracoes']:
    count = s.count('function ' + fn)
    print("  " + fn + ":", count, "definicao(oes)")
