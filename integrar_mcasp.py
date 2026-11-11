p = 'pc_frontend/notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Adicionar um botão para alternar para o modelo MCASP, logo no topo (perto do título)
old_title = '<h1>Notas Explicativas</h1>'
new_title = '''<h1>Notas Explicativas</h1>
    <div style="margin-bottom: 20px;">
        <button id="btn-tradicional" onclick="mostrarTradicional()" style="padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Modelo Tradicional</button>
        <button id="btn-mcasp" onclick="mostrarMCASP()" style="padding: 10px 20px; background: #ccc; color: #333; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-left: 10px;">Modelo MCASP (Novo)</button>
    </div>'''
s = s.replace(old_title, new_title, 1)

# 2. Criar a div do MCASP (inicialmente escondida)
mcasp_div = '''
<div id="tela-mcasp" style="display: none;">
    <div class="aviso" style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
        <b>Rascunho MCASP:</b> Clique em Gerar para preencher automaticamente com os dados reais do período selecionado.
    </div>
    <button onclick="gerarAutoMCASP()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">✨ Gerar Rascunho (Período Atual)</button>
    <div id="formulario-mcasp"><p style="text-align:center;">Carregando estrutura...</p></div>
    <button onclick="salvarMCASP()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 20px;">💾 Salvar Alterações MCASP</button>
</div>
'''

# Insere antes do fechamento do conteudo principal (procura pelo fechamento da div principal)
# Vamos inserir logo apos a div "declaracao-conformidade"
old_decl = '<div id="declaracao-conformidade"'
idx = s.find(old_decl)
if idx != -1:
    s = s[:idx] + mcasp_div + '\n' + s[idx:]
else:
    print("AVISO: Nao achei a div de declaracao, inserindo antes do </body>")
    s = s.replace('</body>', mcasp_div + '\n</body>', 1)

# 3. Adicionar o JavaScript para controlar as abas e as chamadas de API
js_mcasp = '''
<script>
    // Funcoes para alternar entre as abas
    function mostrarTradicional() {
        document.getElementById('tela-mcasp').style.display = 'none';
        document.getElementById('conteudo').style.display = 'block';
        document.getElementById('declaracao-conformidade').style.display = 'none';
        document.getElementById('btn-tradicional').style.background = '#003366';
        document.getElementById('btn-tradicional').style.color = 'white';
        document.getElementById('btn-mcasp').style.background = '#ccc';
        document.getElementById('btn-mcasp').style.color = '#333';
    }

    function mostrarMCASP() {
        document.getElementById('conteudo').style.display = 'none';
        document.getElementById('declaracao-conformidade').style.display = 'none';
        document.getElementById('tela-mcasp').style.display = 'block';
        document.getElementById('btn-mcasp').style.background = '#003366';
        document.getElementById('btn-mcasp').style.color = 'white';
        document.getElementById('btn-tradicional').style.background = '#ccc';
        document.getElementById('btn-tradicional').style.color = '#333';
        carregarMCASP();
    }

    // Funcoes da API do MCASP
    let itensMCASP = [];
    async function carregarMCASP() {
        try {
            const resp = await fetch('/api/notas_mcasp');
            itensMCASP = await resp.json();
            const div = document.getElementById('formulario-mcasp');
            div.innerHTML = '';
            
            itensMCASP.forEach(item => {
                const el = document.createElement('div');
                if (item.nivel == 1) {
                    el.innerHTML = `<h3 style="color: #003366; margin-top: 30px; margin-bottom: 10px; font-size: 18px;">${item.codigo} ${item.titulo}</h3>`;
                    div.appendChild(el);
                } else if (item.nivel == 2) {
                    el.innerHTML = `<h4 style="color: #333; margin-top: 20px; margin-bottom: 10px; font-size: 15px;">${item.codigo} ${item.titulo}</h4>`;
                    div.appendChild(el);
                    const ta = document.createElement('textarea');
                    ta.id = 'txt-mcasp-' + item.id;
                    ta.value = item.texto || '';
                    ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px';
                    div.appendChild(ta);
                } else {
                    el.innerHTML = `<h5 style="color: #444; margin-top: 15px; margin-bottom: 5px; font-size: 14px;">${item.codigo} ${item.titulo}</h5>`;
                    div.appendChild(el);
                    const ta = document.createElement('textarea');
                    ta.id = 'txt-mcasp-' + item.id;
                    ta.value = item.texto || '';
                    ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px';
                    div.appendChild(ta);
                }
            });
        } catch (e) {
            document.getElementById('formulario-mcasp').innerHTML = '<p style="color:red;">Erro ao carregar dados.</p>';
        }
    }

    async function gerarAutoMCASP() {
        if (!confirm("Isso preencherá os campos com os dados reais do período selecionado. Continuar?")) return;
        try {
            const periodo = document.getElementById('periodo').value || '2026-TRIMESTRE-3';
            const resp = await fetch('/api/notas_mcasp/gerar_auto', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ periodo: periodo })
            });
            const r = await resp.json();
            if (r.ok) { alert('Rascunho gerado!'); carregarMCASP(); }
            else { alert('Erro: ' + r.mensagem); }
        } catch (e) { alert('Erro de conexão.'); }
    }

    async function salvarMCASP() {
        const itensParaSalvar = itensMCASP.map(item => {
            const ta = document.getElementById('txt-mcasp-' + item.id);
            return { id: item.id, texto: ta ? ta.value.trim() : (item.texto || '') };
        });
        try {
            const resp = await fetch('/api/notas_mcasp/salvar', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ itens: itensParaSalvar })
            });
            if ((await resp.json()).ok) alert('Salvo com sucesso!');
            else alert('Erro ao salvar.');
        } catch (e) { alert('Erro de conexão.'); }
    }
</script>
'''

if '</body>' not in s:
    s += js_mcasp
else:
    s = s.replace('</body>', js_mcasp + '\n</body>', 1)

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('OK: Tela MCASP integrada na pagina oficial de Notas Explicativas com abas!')
