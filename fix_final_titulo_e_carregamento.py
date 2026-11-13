import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_fix_titulo_vazio")

# 1. Substituir a função renderizarMatriz para corrigir o título
idx_render = html.find("function renderizarMatriz(")
if idx_render != -1:
    i = html.find("{", idx_render)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    novo_render = '''function renderizarMatriz(data, container) {
        if (!container) return;
        
        let matriz = data.matriz || [];
        matriz = normalizarMatriz(matriz);

        if (matriz.length === 0) {
            container.innerHTML = '<div class="loading">Nenhum dado encontrado.</div>';
            return;
        }

        // Tenta pegar o período do JSON, se não tiver, pega dos seletores da tela
        let periodoExibicao = data.periodo;
        if (!periodoExibicao) {
            const ano = document.getElementById('ano')?.value || '';
            const tipo = document.getElementById('tipo_periodo')?.value || '';
            const trimestre = document.getElementById('trimestre')?.value || '';
            periodoExibicao = `${ano}-${tipo}-${trimestre}`;
        }

        // HTML idêntico ao da imagem original
        let html = `
        <div style="background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #003366; font-size: 24px; margin-bottom: 5px;">Matriz de Integridade - ${periodoExibicao}</h3>
            <p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; font-style: italic;">Gerado em: ${new Date().toLocaleString('pt-BR')}</p>
            
            <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px;">
                <thead>
                    <tr style="background-color: #004b8d; color: white; text-align: center;">
                        <th style="padding: 10px; border: 1px solid #ccc;">NOMENCLATURA</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BALANCETE</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BP</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BF</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">BO</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DFC</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DVP</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">DMPL</th>
                        <th style="padding: 10px; border: 1px solid #ccc;">CONF.</th>
                    </tr>
                </thead>
                <tbody>
        `;

        matriz.forEach(m => {
            let confFormatado = m.conf;
            let corConf = '#006400'; // Verde escuro para OK
            
            if (m.conf !== 'OK' && m.conf !== '-') {
                confFormatado = `(${m.conf})`;
                corConf = '#cc0000'; // Vermelho para erros
            }

            html += `
                <tr style="text-align: center; border-bottom: 1px solid #eee;">
                    <td style="padding: 8px; border: 1px solid #ccc; text-align: left; font-weight: bold; color: #333;">${m.item || ''}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.balancete)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bp)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bf)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.bo)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dfc)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dvp)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc;">${formatarMoeda(m.dmpl)}</td>
                    <td style="padding: 8px; border: 1px solid #ccc; font-weight: bold; color: ${corConf};">${confFormatado}</td>
                </tr>
            `;
        });

        html += `</tbody></table></div>`;
        container.innerHTML = html;
    }'''
    html = html[:idx_render] + novo_render + html[i:]

# 2. Corrigir a função verificarEGerar para não ficar travada no carregando
idx_verificar = html.find("async function verificarEGerar(")
if idx_verificar != -1:
    i = html.find("{", idx_verificar)
    contador = 1
    i += 1
    while i < len(html) and contador > 0:
        if html[i] == "{": contador += 1
        elif html[i] == "}": contador -= 1
        i += 1
    
    novo_verificar = '''async function verificarEGerar() {
        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading" style="padding: 20px; color: #004b8d; font-weight: bold;">Carregando a matriz mais recente...</div>';

        try {
            await carregarHistorico();
            
            // Dá uma pequena pausa para garantir que o DOM da lista atualizou
            await new Promise(r => setTimeout(r, 300)); 

            const list = document.getElementById('lista-historico');
            const primeiroCheckbox = list ? list.querySelector('input[type="checkbox"]') : null;
            
            if (primeiroCheckbox) {
                primeiroCheckbox.checked = true;
                await exibirSelecionado(); 
            } else {
                if (container) container.innerHTML = '<div style="padding: 20px; color: #004b8d;">Nenhum histórico encontrado. Verifique o banco de dados.</div>';
            }
        } catch (err) {
            console.error("Erro:", err);
            if (container) container.innerHTML = '<div style="color: red; padding: 20px;">Erro ao carregar a matriz.</div>';
        }
    }'''
    html = html[:idx_verificar] + novo_verificar + html[i:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Título da matriz corrigido e trava de carregamento adicionada!")
