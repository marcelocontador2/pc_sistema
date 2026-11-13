import re

p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Remove qualquer script antigo relacionado ao MCASP (para evitar conflitos)
s = re.sub(r'<script>\s*function alternarAbas.*?</script>', '', s, flags=re.DOTALL)
s = re.sub(r'<script>\s*async function carregarMCASP.*?</script>', '', s, flags=re.DOTALL)
s = re.sub(r'<script>\s*async function gerarAutoMCASP.*?</script>', '', s, flags=re.DOTALL)
s = re.sub(r'<script>\s*async function salvarMCASP.*?</script>', '', s, flags=re.DOTALL)

# Cria o novo JavaScript do zero, sem erros
js_limpo = """
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
        const div = document.getElementById('formulario-mcasp');
        if (!div) return;
        div.innerHTML = '<p>Carregando estrutura...</p>';
        try {
            const resp = await fetch('/api/notas_mcasp');
            const itens = await resp.json();
            div.innerHTML = '';
            itens.forEach(item => {
                const el = document.createElement('div');
                if (item.nivel == 1) {
                    el.innerHTML = '<h3 style="color: #003366; margin-top: 30px;">' + item.codigo + ' ' + item.titulo + '</h3>';
                    div.appendChild(el);
                } else {
                    const heading = item.nivel == 2 ? 'h4' : 'h5';
                    el.innerHTML = '<' + heading + ' style="color: #333; margin-top: 20px;">' + item.codigo + ' ' + item.titulo + '</' + heading + '>';
                    div.appendChild(el);
                    const ta = document.createElement('textarea');
                    ta.id = 'txt-mcasp-' + item.id;
                    ta.value = item.texto || '';
                    ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px'; ta.style.padding = '10px'; ta.style.border = '1px solid #ccc'; ta.style.borderRadius = '4px';
                    div.appendChild(ta);
                }
            });
        } catch (e) {
            div.innerHTML = '<p style="color:red;">Erro ao carregar dados: ' + e.message + '</p>';
        }
    }

    async function gerarAutoMCASP() {
        if (!confirm("Preencher com os dados reais?")) return;
        try {
            const resp = await fetch('/api/notas_mcasp/gerar_auto', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ periodo: '2026-TRIMESTRE-3' })
            });
            if (!resp.ok) throw new Error('Erro ' + resp.status);
            const r = await resp.json();
            if (r.ok) { alert('Rascunho gerado!'); carregarMCASP(); }
            else { alert('Erro: ' + r.mensagem); }
        } catch (e) { alert('Erro ao gerar rascunho: ' + e.message); }
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
"""

# Insere o novo script antes do </body>
if '</body>' in s:
    s = s.replace('</body>', js_limpo + '\n</body>')
else:
    s += js_limpo

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print("OK: JavaScript do frontend reescrito do zero!")
