html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Notas Explicativas</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .aba-ativa { background: #003366 !important; color: white !important; }
        .aba-inativa { background: #ccc !important; color: #333 !important; }
    </style>
</head>
<body>
    <div class="container" style="max-width: 1000px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h1 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px;">Notas Explicativas</h1>
        
        <div style="margin-bottom: 20px; display: flex; gap: 10px;">
            <button id="btn-tradicional" onclick="alternarAbas('tradicional')" class="aba-ativa" style="padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Modelo Tradicional</button>
            <button id="btn-mcasp" onclick="alternarAbas('mcasp')" class="aba-inativa" style="padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Modelo MCASP (Novo)</button>
        </div>

        <!-- TELA TRADICIONAL -->
        <div id="conteudo-tradicional">
            <div style="display: flex; gap: 15px; margin-bottom: 20px; background: #f8f9fa; padding: 15px; border-radius: 4px; border: 1px solid #ddd;">
                <div><label>Ano:</label><select id="ano" style="padding: 5px;"><option>2026</option></select></div>
                <div><label>Tipo:</label><select id="tipo" style="padding: 5px;"><option>Trimestral</option></select></div>
                <div><label>Período:</label><select id="periodo" style="padding: 5px;"><option>3º</option></select></div>
                <button onclick="alert('Verificando dados...')" style="background: #003366; color: white; padding: 5px 15px; border: none; border-radius: 4px;">Verificar Dados</button>
            </div>
            <p style="text-align: center; color: #666;">Notas Explicativas do Modelo Tradicional carregadas aqui.</p>
        </div>

        <!-- TELA MCASP -->
        <div id="conteudo-mcasp" style="display: none;">
            <div style="display: flex; gap: 15px; margin-bottom: 20px; background: #f8f9fa; padding: 15px; border-radius: 4px; border: 1px solid #ddd;">
                <div><label>Ano:</label><select id="ano-mcasp" style="padding: 5px;"><option>2026</option></select></div>
                <div><label>Tipo:</label><select id="tipo-mcasp" style="padding: 5px;"><option>Trimestral</option></select></div>
                <div><label>Período:</label><select id="periodo-mcasp" style="padding: 5px;"><option>3º</option></select></div>
                <button onclick="alert('Verificando dados...')" style="background: #003366; color: white; padding: 5px 15px; border: none; border-radius: 4px;">Verificar Dados</button>
            </div>
            
            <div class="aviso" style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px; border-radius: 4px;">
                <b>Rascunho MCASP:</b> Clique em Gerar para preencher automaticamente com os dados reais do período selecionado.
            </div>
            <button onclick="gerarAutoMCASP()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-bottom: 20px;">✨ Gerar Rascunho (Período Atual)</button>
            <div id="formulario-mcasp"><p style="text-align: center;">Carregando estrutura do MCASP...</p></div>
            <button onclick="salvarMCASP(); salvarHistoricoMCASP()" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 20px;">💾 Salvar no Histórico MCASP</button>
        </div>
    </div>

    <script>
        function alternarAbas(aba) {
            const telaTrad = document.getElementById('conteudo-tradicional');
            const telaMCASP = document.getElementById('conteudo-mcasp');
            const btnTrad = document.getElementById('btn-tradicional');
            const btnMCASP = document.getElementById('btn-mcasp');

            if (aba === 'mcasp') {
                telaTrad.style.display = 'none';
                telaMCASP.style.display = 'block';
                btnTrad.className = 'aba-inativa';
                btnMCASP.className = 'aba-ativa';
                carregarMCASP();
            } else {
                telaTrad.style.display = 'block';
                telaMCASP.style.display = 'none';
                btnTrad.className = 'aba-ativa';
                btnMCASP.className = 'aba-inativa';
            }
        }

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
                    } else {
                        const heading = item.nivel == 2 ? 'h4' : 'h5';
                        el.innerHTML = `<${heading} style="color: #333; margin-top: 20px; margin-bottom: 10px; font-size: 15px;">${item.codigo} ${item.titulo}</${heading}>`;
                        div.appendChild(el);
                        const ta = document.createElement('textarea');
                        ta.id = 'txt-mcasp-' + item.id;
                        ta.value = item.texto || '';
                        ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px'; ta.style.borderRadius = '4px'; ta.style.border = '1px solid #ccc'; ta.style.padding = '10px';
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
                const periodo = document.getElementById('periodo-mcasp').value || '2026-TRIMESTRE-3';
                const resp = await fetch('/api/notas_mcasp/gerar_auto', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ periodo: periodo })
                });
                if ((await resp.json()).ok) { alert('Rascunho gerado com sucesso!'); carregarMCASP(); }
            } catch (e) { alert('Erro de conexão.'); }
        }

        async function salvarMCASP() {
            const itensParaSalvar = itensMCASP.map(item => {
                const ta = document.getElementById('txt-mcasp-' + item.id);
                return { id: item.id, texto: ta ? ta.value.trim() : (item.texto || '') };
            });
            try { await fetch('/api/notas_mcasp/salvar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ itens: itensParaSalvar }) }); } catch(e) {}
        }

        async function salvarHistoricoMCASP() {
            try {
                const periodo = document.getElementById('periodo-mcasp').value || '2026-TRIMESTRE-3';
                const resp = await fetch('/api/notas_mcasp/salvar_historico', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ periodo: periodo })
                });
                if ((await resp.json()).ok) {
                    alert('Histórico do Modelo MCASP salvo com sucesso!');
                }
            } catch(e) { alert('Erro de conexão.'); }
        }
    </script>
</body>
</html>"""

# Salva o arquivo forçando UTF-8 sem BOM
with open('pc_frontend/notas_explicativas.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print('OK: Arquivo HTML reescrito do zero, sem corrupcao e com abas perfeitas.')
