
                let dadosImportados = [];
                function carregarImportados() {
                    fetch('/api/relatorios_importados')
                        .then(r => r.json())
                        .then(data => { dadosImportados = data || []; filtrarTabela(); })
                        .catch(err => { document.getElementById('lista-importados').innerHTML = '<tr><td colspan="4" style="padding: 10px; text-align: center; color: red;">Erro ao carregar os relatórios.</td></tr>'; });
                }
                function filtrarTabela() {
                    const termo = document.getElementById('busca-relatorio').value.toLowerCase();
                    const tbody = document.getElementById('lista-importados');
                    const filtrados = dadosImportados.filter(item => item.nome.toLowerCase().includes(termo) || item.tipo.toLowerCase().includes(termo) || item.periodo.toLowerCase().includes(termo));
                    if (filtrados.length === 0) { tbody.innerHTML = '<tr><td colspan="4" style="padding: 10px; text-align: center;">Nenhum relatório encontrado.</td></tr>'; return; }
                    let html = '';
                    filtrados.forEach(item => {
                        html += `<tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">${item.nome}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">${item.tipo}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">${item.periodo}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                                <div style="display: flex; gap: 5px; justify-content: center;">
                                    <button onclick="gerarPdfLista('${item.tipo}')" style="padding: 5px 10px; background: #0056b3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">PDF</button>
                                    <button onclick="excluirRelatorio('${item.nome}')" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Excluir</button>
                                </div>
                            </td>
                        </tr>`;
                    });
                    tbody.innerHTML = html;
                }
                function gerarPdfLista(tipo) { window.open('/download/pdf/' + tipo, '_blank'); }
                function excluirRelatorio(nomeArquivo) {
                    if (!confirm("Excluir " + nomeArquivo + "?")) return;
                    fetch('/api/excluir_relatorio/' + nomeArquivo, { method: 'DELETE' })
                    .then(r => r.json()).then(data => { if (data.erro) alert(data.mensagem); else { alert("Excluído!"); carregarImportados(); } })
                    .catch(err => alert("Erro de conexão."));
                }
                document.addEventListener("DOMContentLoaded", carregarImportados);
            