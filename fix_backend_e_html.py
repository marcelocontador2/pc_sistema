import re

# 1. Corrige o main.py para não corromper o JSON do histórico
p = 'pc_backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Procura a rota do histórico e adiciona o ensure_ascii=False se estiver faltando
# e verifica se há decodificação errada (latin1/utf8)
if 'def historico_notas_explicativas():' in s:
    # Substitui a função inteira por uma versão limpa e segura
    padrao = re.compile(r'@app\.get\("/historico_notas_explicativas"\).*?return \[.*?\n', re.DOTALL)
    nova_rota = '''@app.get("/historico_notas_explicativas")
async def historico_notas_explicativas():
    import sqlite3, os, json
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pc_storage", "banco_dados.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, periodo, data_geracao FROM historico_notas_explicativas ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    # Retorna os dados como lista de dicionários limpos
    return [{"id": r[0], "periodo": r[1], "data_geracao": r[2]} for r in rows]

'''
    if padrao.search(s):
        s = padrao.sub(nova_rota, s, count=1)
        print("OK: Rota do historico corrigida no backend.")
    else:
        print("Aviso: Não foi possível substituir a rota exata, mas o código foi mantido.")

# 2. Corrige o HTML (injetando o JS das abas corretamente sem apagar o resto)
p_html = 'pc_frontend/notas_explicativas.html'
with open(p_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Verifica se as abas já estão lá, se não, insere de forma limpa
if 'id="btn-tradicional"' not in html:
    html = html.replace('<h1>Notas Explicativas</h1>', '''<h1>Notas Explicativas</h1>
    <div style="margin-bottom: 20px;">
        <button id="btn-tradicional" onclick="alternarAbas('tradicional')" style="padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Modelo Tradicional</button>
        <button id="btn-mcasp" onclick="alternarAbas('mcasp')" style="padding: 10px 20px; background: #ccc; color: #333; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-left: 10px;">Modelo MCASP (Novo)</button>
    </div>''', 1)

# Envolve o conteúdo original (se ainda não estiver envolvido)
if 'id="conteudo-tradicional"' not in html:
    html = html.replace('<div id="declaracao-conformidade"', '<div id="conteudo-tradicional">\n<div id="declaracao-conformidade"', 1)
    html = html.replace('</body>', '</div>\n</body>', 1) # Fecha a div antes do body

# Insere o container do MCASP e o JS, se não existirem
if 'id="tela-mcasp"' not in html:
    mcasp_div = '''
    <div id="tela-mcasp" style="display: none; margin-top: 20px;">
        <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px; border-radius: 4px;">
            <b>Rascunho MCASP:</b> Clique em Gerar para preencher com os dados reais.
        </div>
        <button onclick="gerarAutoMCASP()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">✨ Gerar Rascunho</button>
        <div id="formulario-mcasp"><p>Carregando...</p></div>
        <button onclick="salvarMCASP()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 20px;">💾 Salvar Alterações</button>
    </div>
    '''
    html = html.replace('</body>', mcasp_div + '\n</body>', 1)

    js_abas = '''
    <script>
        function alternarAbas(aba) {
            const telaTrad = document.getElementById('conteudo-tradicional');
            const telaMCASP = document.getElementById('tela-mcasp');
            const btnTrad = document.getElementById('btn-tradicional');
            const btnMCASP = document.getElementById('btn-mcasp');

            if (aba === 'mcasp') {
                if (telaTrad) telaTrad.style.display = 'none';
                if (telaMCASP) telaMCASP.style.display = 'block';
                if (btnTrad) { btnTrad.style.background = '#ccc'; btnTrad.style.color = '#333'; }
                if (btnMCASP) { btnMCASP.style.background = '#003366'; btnMCASP.style.color = 'white'; }
                carregarMCASP();
            } else {
                if (telaTrad) telaTrad.style.display = 'block';
                if (telaMCASP) telaMCASP.style.display = 'none';
                if (btnTrad) { btnTrad.style.background = '#003366'; btnTrad.style.color = 'white'; }
                if (btnMCASP) { btnMCASP.style.background = '#ccc'; btnMCASP.style.color = '#333'; }
            }
        }

        async function carregarMCASP() {
            try {
                const resp = await fetch('/api/notas_mcasp');
                const itens = await resp.json();
                const div = document.getElementById('formulario-mcasp');
                div.innerHTML = '';
                itens.forEach(item => {
                    const el = document.createElement('div');
                    if (item.nivel == 1) {
                        el.innerHTML = `<h3 style="color: #003366; margin-top: 30px;">${item.codigo} ${item.titulo}</h3>`;
                        div.appendChild(el);
                    } else {
                        el.innerHTML = `<h4 style="color: #333; margin-top: 20px;">${item.codigo} ${item.titulo}</h4>`;
                        div.appendChild(el);
                        const ta = document.createElement('textarea');
                        ta.id = 'txt-mcasp-' + item.id;
                        ta.value = item.texto || '';
                        ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px';
                        div.appendChild(ta);
                    }
                });
            } catch (e) { document.getElementById('formulario-mcasp').innerHTML = '<p style="color:red;">Erro ao carregar dados.</p>'; }
        }

        async function gerarAutoMCASP() {
            if (!confirm("Preencher com os dados reais?")) return;
            try {
                const periodo = '2026-TRIMESTRE-3';
                const resp = await fetch('/api/notas_mcasp/gerar_auto', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ periodo: periodo })
                });
                if ((await resp.json()).ok) { alert('Rascunho gerado!'); carregarMCASP(); }
            } catch (e) { alert('Erro de conexão.'); }
        }

        async function salvarMCASP() {
            const itens = Array.from(document.querySelectorAll('#formulario-mcasp textarea')).map(ta => {
                const id = ta.id.replace('txt-mcasp-', '');
                return { id: parseInt(id), texto: ta.value.trim() };
            });
            try {
                await fetch('/api/notas_mcasp/salvar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ itens: itens }) });
                alert('Salvo com sucesso!');
            } catch(e) { alert('Erro ao salvar.'); }
        }
    </script>
    '''
    html = html.replace('</body>', js_abas + '\n</body>', 1)

with open(p_html, 'w', encoding='utf-8') as f:
    f.write(html)
print("OK: HTML e JS atualizados com sucesso.")
