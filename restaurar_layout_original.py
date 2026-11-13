import re
import shutil

caminho = "pc_frontend/integridade.html"

with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

shutil.copy(caminho, caminho + ".bak_layout_original_exato")

# 1. Encontra o início e fim do bloco <script> atual para substituí-lo
idx_inicio = html.find("<script>")
idx_fim = html.find("</script>", idx_inicio) + len("</script>")

novo_script = '''<script>
    let dadosAtuais = null;

    function formatarMoeda(valor) {
        if (valor === null || valor === undefined || valor === '-' || valor === '') return '-';
        // Se já for string formatada, retorna
        if (typeof valor === 'string' && valor.includes('R$')) return valor;
        return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function getHistoricoSelecionado() {
        const checkboxes = document.querySelectorAll('#lista-historico input[type="checkbox"]');
        for (let cb of checkboxes) {
            if (cb.checked) return cb.value;
        }
        return null;
    }

    document.addEventListener("DOMContentLoaded", () => {
        carregarHistorico();
    });

    function carregarHistorico() {
        const list = document.getElementById('lista-historico');
        if (!list) return;
        list.innerHTML = '<li class="loading">Carregando histórico...</li>';
        fetch(`/historico_integridade_matriz?_t=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                list.innerHTML = '';
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(h => {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <input type="checkbox" value="${h.id}">
                            <span>Período: ${h.periodo} | Gerado em: ${h.data_geracao || h.criado_em || 'N/A'}</span>
                        `;
                        list.appendChild(li);
                    });
                } else {
                    list.innerHTML = '<li>Nenhum histórico salvo.</li>';
                }
            })
            .catch(err => {
                list.innerHTML = '<li>Erro ao carregar histórico.</li>';
                console.error(err);
            });
    }

    // Converte qualquer formato (novo ou antigo) para o formato exato da tabela azul
    function normalizarMatriz(matriz) {
        if (!matriz || matriz.length === 0) return [];
        if ('balancete' in matriz[0]) return matriz; // Já está no formato antigo

        return matriz.map(m => {
            // Mapeia o formato novo para o antigo
            return {
                item: m.descricao || m.nomenclatura || m.item || '',
                balancete: m.valor_balancete || m.valor || '-',
                bp: m.valor_bp || '-',
                bf: m.valor_bf || '-',
                bo: m.valor_bo || '-',
                dfc: m.valor_dfc || '-',
                dvp: m.valor_dvp || '-',
                dmpl: m.valor_dmpl || '-',
                conf: m.consistente === false ? (m.codigo_erro || '(1)') : (m.observacao && m.observacao !== 'OK' ? m.observacao : 'OK')
            };
        });
    }

    async function verificarEGerar() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        const container = document.getElementById('integridade-cards');
        if (container) container.innerHTML = '<div class="loading">Gerando matriz...</div>';

        try {
            const res = await fetch(`/api/integridade_matriz/${periodo}?_t=${Date.now()}`);
            const data = await res.json();

            if (data.erro) {
                alert("Aviso: " + data.mensagem);
                if (container) container.innerHTML = '';
                return;
            }

            dadosAtuais = data;
            renderizarMatriz(data, container);
        } catch (err) {
            console.error(err);
            if (container) container.innerHTML = '<div class="loading">Erro ao buscar dados.</div>';
        }
    }

    function renderizarMatriz(data, container) {
        if (!container) return;
        
        let matriz = data.matriz || [];
        matriz = normalizarMatriz(matriz);

        if (matriz.length === 0) {
            container.innerHTML = '<div class="loading">Nenhum dado encontrado.</div>';
            return;
        }

        // HTML idêntico ao da imagem original
        let html = `
        <div style="background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #003366; font-size: 24px; margin-bottom: 5px;">Matriz de Integridade - ${data.periodo || ''}</h3>
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
            // Verifica se o status é OK ou número de erro
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
    }

    async function exibirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }

        try {
            const res = await fetch(`/historico_integridade_matriz/${id}`);
            const data = await res.json();

            if (data.erro) { alert("Erro: " + data.mensagem); return; }

            let payload = data.dados ? data.dados : data;
            if (typeof payload === 'string') {
                try { payload = JSON.parse(payload); } catch(e) {}
            }

            dadosAtuais = payload;
            const container = document.getElementById('integridade-cards');
            renderizarMatriz(payload, container);
        } catch (err) {
            alert("Erro ao carregar histórico: " + err);
        }
    }

    function gerarPDF() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        window.open(`/gerar_pdf_integridade/${id}`, '_blank');
    }

    function salvarMatriz() {
        const ano = document.getElementById('ano').value;
        const tipo = document.getElementById('tipo_periodo').value;
        const trimestre = document.getElementById('trimestre').value;
        const periodo = `${ano}-${tipo}-${trimestre}`;

        fetch(`/api/integridade_matriz/${periodo}/salvar`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.erro) {
                    alert("Erro: " + data.mensagem);
                } else {
                    alert("Salvo com sucesso!");
                    window.location.reload();
                }
            })
            .catch(err => alert("Erro ao salvar: " + err));
    }

    function excluirSelecionado() {
        const id = getHistoricoSelecionado();
        if (!id) { alert("Selecione um histórico na lista."); return; }
        if (!confirm("Tem certeza que deseja excluir o histórico selecionado?")) return;

        fetch("/excluir_multiplos_integridade_matriz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids: [id] })
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                carregarHistorico();
            } else {
                alert("Erro ao excluir: " + (data.mensagem || "Erro desconhecido"));
            }
        })
        .catch(err => alert("Erro ao excluir: " + err));
    }

    function fecharModalJust() {
        const modal = document.getElementById('modalJustificativa');
        if (modal) modal.style.display = 'none';
    }

    function salvarJustificativa() {
        alert("Justificativa salva (função em desenvolvimento).");
        fecharModalJust();
    }
</script>'''

# Substitui o bloco no HTML
html = html[:idx_inicio] + novo_script + html[idx_fim:]

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Script substituído com SUCESSO!")
print("✅ O layout da tabela azul (conforme sua imagem) foi restaurado com força total.")
