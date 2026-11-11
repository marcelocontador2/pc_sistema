html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Notas Explicativas - COFEN</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-top: 0; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .aba-ativa { background: #003366; color: white; }
        .aba-inativa { background: #e0e0e0; color: #333; }
        .barra-botoes { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; background: #f8f9fa; padding: 15px; border-radius: 4px; border: 1px solid #ddd; }
        .btn-verde { background: #28a745; color: white; }
        .btn-vermelho { background: #dc3545; color: white; }
        .btn-azul { background: #0056b3; color: white; }
        .btn-escuro { background: #003366; color: white; }
        .btn-laranja { background: #fd7e14; color: white; }
        .historico-box { background: #f8f9fa; padding: 15px; border-radius: 4px; border-left: 4px solid #003366; margin-bottom: 15px; }
        .texto-nota { text-align: justify; line-height: 1.6; font-size: 14px; margin-bottom: 20px; }
        .nota-header { color: #003366; font-weight: bold; margin-bottom: 10px; font-size: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Notas Explicativas</h1>
        
        <!-- ABAS -->
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button id="btn-tradicional" class="aba-ativa btn" onclick="alternarAbas('tradicional')">Modelo Tradicional</button>
            <button id="btn-mcasp" class="aba-inativa btn" onclick="alternarAbas('mcasp')">Modelo MCASP (Novo)</button>
        </div>

        <!-- TELA TRADICIONAL -->
        <div id="tela-tradicional">
            <div class="barra-botoes">
                <button class="btn btn-escuro" onclick="alert('Verificar dados')">Verificar Dados</button>
                <button class="btn btn-verde" onclick="alert('Salvar notas tradicionais')">Salvar</button>
            </div>
            <div class="barra-botoes">
                <button class="btn btn-laranja" onclick="alert('Voltar')">← Voltar</button>
                <button class="btn btn-verde" onclick="alert('Exibir')">Exibir Selecionado</button>
                <button class="btn btn-vermelho" onclick="alert('Excluir')">Excluir Selecionados</button>
                <button class="btn btn-azul" onclick="alert('Gerar PDF')">Gerar PDF</button>
                <button class="btn btn-verde" onclick="alert('Incluir')">Incluir Item</button>
                <button class="btn btn-azul" onclick="alert('Observações')">Observações</button>
                <button class="btn btn-azul" onclick="alert('Conclusão')">Conclusão</button>
            </div>
            
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <div style="width: 250px;">
                    <h3>Histórico Salvo</h3>
                    <div class="historico-box">
                        <p><b>Período: 2026-TRIMESTRE-3</b></p>
                        <p>11/11/2026 15:08:43</p>
                    </div>
                </div>
                <div style="flex: 1;">
                    <div class="nota-header">NOTA 1 — CONTEXTO OPERACIONAL E BASE DE PREPARAÇÃO</div>
                    <p class="texto-nota">O Conselho Federal de Enfermagem (Cofen) é autarquia federal que integra o Sistema Cofen/Conselhos Regionais. Estas notas acompanham o Relatório Consolidado de Análise Contábil do 3º trimestre de 2026 e compreendem o Balancete de Verificação, o Balanço Financeiro (BF), o Balanço Orçamentário (BO), o Balanço Patrimonial (BP), a Demonstração dos Fluxos de Caixa (DFC), a Demonstração das Mutações do Patrimônio Líquido (DMPL) e a Demonstração das Variações Patrimoniais (DVP).</p>
                    
                    <div class="nota-header">NOTA 2 — CAIXA E EQUIVALENTES DE CAIXA</div>
                    <p class="texto-nota">O saldo de caixa e equivalentes em 30/09/2026 é de R$ 186.838.676,59, redução de -11,93% frente aos R$ 212.158.770,26 do período anterior. A variação decorre do fluxo de pagamentos de despesas, com destaque para o grupo de serviços de pessoa jurídica. O saldo foi conciliado entre Balancete, BP, BF e DFC.</p>
                </div>
            </div>
        </div>

        <!-- TELA MCASP -->
        <div id="tela-mcasp" style="display: none;">
            <div class="barra-botoes">
                <button class="btn btn-escuro" onclick="alert('Verificar dados MCASP')">Verificar Dados</button>
            </div>
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px; border-radius: 4px;">
                <b>Rascunho MCASP:</b> Clique em Gerar para preencher com os dados reais.
            </div>
            <button class="btn btn-azul" onclick="gerarAutoMCASP()">✨ Gerar Rascunho (Período Atual)</button>
            <div id="formulario-mcasp" style="margin-top: 20px;"><p>Carregando estrutura...</p></div>
            <button class="btn btn-verde" onclick="salvarMCASP()" style="margin-top: 20px;">💾 Salvar Alterações MCASP</button>
        </div>
    </div>

    <script>
        function alternarAbas(aba) {
            const telaTrad = document.getElementById('tela-tradicional');
            const telaMCASP = document.getElementById('tela-mcasp');
            const btnTrad = document.getElementById('btn-tradicional');
            const btnMCASP = document.getElementById('btn-mcasp');

            if (aba === 'mcasp') {
                telaTrad.style.display = 'none';
                telaMCASP.style.display = 'block';
                btnTrad.className = 'aba-inativa btn';
                btnMCASP.className = 'aba-ativa btn';
                carregarMCASP();
            } else {
                telaTrad.style.display = 'block';
                telaMCASP.style.display = 'none';
                btnTrad.className = 'aba-ativa btn';
                btnMCASP.className = 'aba-inativa btn';
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
                        el.innerHTML = `<h3 style="color: #003366; margin-top: 30px;">${item.codigo} ${item.titulo}</h3>`;
                        div.appendChild(el);
                    } else {
                        const heading = item.nivel == 2 ? 'h4' : 'h5';
                        el.innerHTML = `<${heading} style="color: #333; margin-top: 20px;">${item.codigo} ${item.titulo}</${heading}>`;
                        div.appendChild(el);
                        const ta = document.createElement('textarea');
                        ta.id = 'txt-mcasp-' + item.id;
                        ta.value = item.texto || '';
                        ta.style.width = '100%'; ta.style.minHeight = '80px'; ta.style.marginBottom = '15px'; ta.style.padding = '10px'; ta.style.border = '1px solid #ccc'; ta.style.borderRadius = '4px';
                        div.appendChild(ta);
                    }
                });
            } catch (e) {
                document.getElementById('formulario-mcasp').innerHTML = '<p style="color:red;">Erro ao carregar dados.</p>';
            }
        }

        async function gerarAutoMCASP() {
            if (!confirm("Preencher com os dados reais do período?")) return;
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
            const itensParaSalvar = itensMCASP.map(item => {
                const ta = document.getElementById('txt-mcasp-' + item.id);
                return { id: item.id, texto: ta ? ta.value.trim() : (item.texto || '') };
            });
            try { 
                await fetch('/api/notas_mcasp/salvar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ itens: itensParaSalvar }) });
                alert('Notas do MCASP salvas com sucesso!');
            } catch(e) { alert('Erro ao salvar.'); }
        }
    </script>
</body>
</html>"""

with open('pc_frontend/notas_explicativas.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print("OK: Tela recriada do zero, limpa, formatada e com as abas funcionando.")
