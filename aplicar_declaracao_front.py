p = 'pc_frontend/notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 1) Substituir os 5 paragrafos fixos por um container dinamico + botao incluir
ini_ancora = '<h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-top: 0; margin-bottom: 20px; font-size: 15px; text-transform: uppercase;">Declara'
fim_ancora = '<div style="margin-top: 50px; text-align: center;">'

idx_ini = s.find(ini_ancora)
idx_fim = s.find(fim_ancora, idx_ini)

if idx_ini == -1 or idx_fim == -1:
    print('ERRO: ancoras nao encontradas')
    raise SystemExit(1)

# Preservar o <h3> inteiro
fim_h3 = s.find('</h3>', idx_ini) + len('</h3>')
h3_completo = s[idx_ini:fim_h3]

novo_bloco = h3_completo + '''
        <div id="itens-declaracao-container" style="margin-top: 15px;">
            <p style="text-align:center; color:#666;">Carregando itens...</p>
        </div>
        <button type="button" onclick="abrirModalIncluirDeclaracao()" style="margin-top: 15px; padding: 8px 16px; background: #003366; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 13px;">➕ Incluir Item</button>
        
        '''

s = s[:idx_ini] + novo_bloco + s[idx_fim:]
print('OK: bloco HTML dinamico injetado')

# 2) Injetar modal + JS antes do </body>
js_e_modal = '''
<!-- MODAL DECLARACAO -->
<div id="modal-declaracao" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; justify-content:center; align-items:center;">
    <div style="background:#fff; padding:25px; border-radius:8px; width:90%; max-width:600px;">
        <h3 id="modal-decl-titulo" style="margin-top:0; color:#003366;">Item da Declaração</h3>
        <textarea id="modal-decl-texto" style="width:100%; height:120px; padding:10px; border:1px solid #ccc; border-radius:4px; font-family:inherit; font-size:13px;" placeholder="Digite o texto do item..."></textarea>
        <input type="hidden" id="modal-decl-id">
        <div style="margin-top:15px; text-align:right;">
            <button type="button" onclick="fecharModalDeclaracao()" style="padding:8px 16px; margin-right:8px; background:#ccc; border:none; border-radius:4px; cursor:pointer;">Cancelar</button>
            <button type="button" onclick="salvarItemDeclaracao()" style="padding:8px 16px; background:#003366; color:#fff; border:none; border-radius:4px; cursor:pointer;">Salvar</button>
        </div>
    </div>
</div>

<script>
async function carregarItensDeclaracao() {
    const container = document.getElementById('itens-declaracao-container');
    if (!container) return;
    try {
        const resp = await fetch('/api/declaracao_conformidade');
        const itens = await resp.json();
        if (!itens || itens.length === 0) {
            container.innerHTML = '<p style="color:#999;">Nenhum item cadastrado.</p>';
            return;
        }
        let html = '';
        itens.forEach((item, idx) => {
            html += `<div style="display:flex; gap:10px; margin-bottom:12px; align-items:flex-start; justify-content:space-between;">
                <p style="text-align: justify; line-height: 1.6; font-size: 13px; margin: 0; flex: 1;"><b>${idx+1}.</b> ${item.texto}</p>
                <div style="display:flex; gap:5px; flex-shrink:0;">
                    <button onclick="abrirModalEditarDeclaracao(${item.id})" title="Editar" style="background:none; border:none; cursor:pointer; font-size:16px;">✏️</button>
                    <button onclick="excluirItemDeclaracao(${item.id})" title="Excluir" style="background:none; border:none; cursor:pointer; font-size:16px;">🗑️</button>
                </div>
            </div>`;
        });
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = '<p style="color:red;">Erro ao carregar itens: ' + e.message + '</p>';
    }
}

function abrirModalIncluirDeclaracao() {
    document.getElementById('modal-decl-titulo').innerText = 'Incluir Item na Declaração';
    document.getElementById('modal-decl-texto').value = '';
    document.getElementById('modal-decl-id').value = '';
    document.getElementById('modal-declaracao').style.display = 'flex';
}

async function abrirModalEditarDeclaracao(id) {
    try {
        const resp = await fetch('/api/declaracao_conformidade');
        const itens = await resp.json();
        const item = itens.find(i => i.id === id);
        if (!item) return alert('Item não encontrado');
        document.getElementById('modal-decl-titulo').innerText = 'Editar Item da Declaração';
        document.getElementById('modal-decl-texto').value = item.texto;
        document.getElementById('modal-decl-id').value = item.id;
        document.getElementById('modal-declaracao').style.display = 'flex';
    } catch(e) { alert('Erro: ' + e.message); }
}

function fecharModalDeclaracao() {
    document.getElementById('modal-declaracao').style.display = 'none';
}

async function salvarItemDeclaracao() {
    const id = document.getElementById('modal-decl-id').value;
    const texto = document.getElementById('modal-decl-texto').value.trim();
    if (!texto) return alert('Texto vazio');
    try {
        const url = id ? '/api/declaracao_conformidade/' + id : '/api/declaracao_conformidade';
        const method = id ? 'PUT' : 'POST';
        const resp = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({texto: texto})
        });
        const r = await resp.json();
        if (r.ok) {
            fecharModalDeclaracao();
            carregarItensDeclaracao();
        } else {
            alert('Erro: ' + (r.mensagem || 'desconhecido'));
        }
    } catch(e) { alert('Erro: ' + e.message); }
}

async function excluirItemDeclaracao(id) {
    if (!confirm('Tem certeza que deseja excluir este item?')) return;
    try {
        const resp = await fetch('/api/declaracao_conformidade/' + id, { method: 'DELETE' });
        const r = await resp.json();
        if (r.ok) carregarItensDeclaracao();
        else alert('Erro ao excluir');
    } catch(e) { alert('Erro: ' + e.message); }
}

document.addEventListener('DOMContentLoaded', () => {
    const obs = new MutationObserver(() => {
        const el = document.getElementById('declaracao-conformidade');
        if (el && el.style.display !== 'none' && !el.dataset.loaded) {
            el.dataset.loaded = '1';
            carregarItensDeclaracao();
        }
    });
    obs.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['style'] });
});
</script>
</body>'''

if '</body>' not in s:
    print('ERRO: </body> nao encontrado')
    raise SystemExit(1)

if 'modal-declaracao' in s:
    print('AVISO: modal ja existe, pulando')
else:
    s = s.replace('</body>', js_e_modal, 1)
    print('OK: modal + JS injetados')

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('notas_explicativas.html atualizado')
