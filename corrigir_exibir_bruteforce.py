import re, shutil, datetime

arquivo = r"pc_frontend\panorama.html"
backup = f"pc_frontend\\panorama_backup_exibir_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(arquivo, backup)
print(f"[OK] Backup: {backup}\n")

with open(arquivo, "r", encoding="utf-8") as f:
    html = f.read()

# Substitui as duas funções responsáveis pelo Exibir e pelo preenchimento
novo_js = """
        // ===== FUNÇÕES CORE =====
        const fmt = (val) => {
            if (val === undefined || val === null) return 'R$ 0,0 mi';
            let num = parseFloat(val);
            if (isNaN(num)) return 'R$ 0,0 mi';
            
            let absNum = Math.abs(num) / 1000000;
            let sinal = num < 0 ? '-R$ ' : 'R$ ';
            return sinal + absNum.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' mi';
        };

        function aplicarValores(data) {
            // Desembrulha o JSON se ele vier dentro de "dados" ou for uma string
            let d = data;
            if (d && d.dados) d = d.dados;
            if (typeof d === 'string') {
                try { d = JSON.parse(d); } catch(e) {}
            }
            if (d && d.dados) d = d.dados;

            console.log("Dados recebidos para os cards:", d);

            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = fmt(val);
            };

            setVal('val-caixa', d.caixa_bp);
            setVal('val-ativo', d.ativo_total);
            setVal('val-passivo', d.passivo_total);
            setVal('val-pl', d.patrimonio_liquido);
            setVal('val-receitas', d.receita_realizada);
            setVal('val-despesas', d.despesa_empenhada);
            setVal('val-superavit-orc', d.superavit_orcamentario);
            setVal('val-superavit-pat', d.superavit_patrimonial);
            setVal('val-superavit-fin', d.superavit_financeiro);
        }

        async function carregarPanorama() {
            const ano = document.getElementById('ano').value;
            const tipo = document.getElementById('tipo_periodo').value;
            const valor = document.getElementById('trimestre').value;
            const periodo = `${ano}-${tipo}-${valor}`;
            
            document.getElementById('periodo-titulo').innerText = `Resultados Gerais — ${valor}º Trimestre de ${ano}`;
            
            try {
                const response = await fetch(`/api/panorama/${periodo}`);
                const data = await response.json();
                
                if (data.erro) { alert("Erro: " + (data.mensagem || "Faltam peças")); return; }
                
                aplicarValores(data);
                
                const btnSalvar = document.getElementById("btn-salvar");
                btnSalvar.setAttribute("data-periodo", periodo);
                btnSalvar.style.display = "inline-block";
                btnSalvar.innerText = "Confirmar e Salvar";
                btnSalvar.disabled = false;
            } catch (e) { 
                console.error(e); 
                alert("Erro de conexão ao buscar panorama.");
            }
        }

        async function salvarPanorama() {
            const btn = document.getElementById("btn-salvar");
            const periodo = btn.getAttribute("data-periodo");
            if (!periodo) { alert("Verifique o panorama antes de salvar."); return; }
            
            const dadosTela = {
                ativo_total:      document.getElementById('val-ativo').innerText,
                passivo_total:    document.getElementById('val-passivo').innerText,
                patrimonio_liquido: document.getElementById('val-pl').innerText,
                caixa_bp:         document.getElementById('val-caixa').innerText,
                receita_realizada: document.getElementById('val-receitas').innerText,
                despesa_empenhada: document.getElementById('val-despesas').innerText,
                superavit_orcamentario: document.getElementById('val-superavit-orc').innerText,
                superavit_patrimonial:  document.getElementById('val-superavit-pat').innerText,
                superavit_financeiro:   document.getElementById('val-superavit-fin').innerText
            };
            
            btn.innerText = "Salvando..."; 
            btn.disabled = true;
            
            try {
                const res = await fetch("/salvar_panorama/" + periodo, { 
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dadosTela)
                });
                if(res.ok) {
                    alert("Resultados salvos com sucesso!");
                    carregarHistorico();
                } else {
                    alert("Erro no servidor ao salvar.");
                }
            } catch (e) { 
                alert("Erro de conexão ao salvar."); 
            } finally { 
                btn.innerText = "Confirmar e Salvar"; 
                btn.disabled = false; 
            }
        }

        function carregarHistorico() {
            fetch('/historico_panorama')
                .then(r => r.json())
                .then(data => {
                    let html = '';
                    if (!data || data.length === 0) {
                        html = '<li>Nenhum histórico.</li>';
                    } else {
                        data.forEach(item => {
                            html += `<li>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <input type="checkbox" class="check-historico" value="${item.id}">
                                    <div>
                                        <div class="periodo">${item.periodo}</div>
                                        <div class="data">Gerado em: ${item.data_geracao}</div>
                                    </div>
                                </div>
                            </li>`;
                        });
                    }
                    document.getElementById('lista-historico').innerHTML = html;
                })
                .catch(e => console.error("Erro no historico", e));
        }

        async function exibirSelecionado() {
            let check = document.querySelector('.check-historico:checked');
            if (!check) {
                // Fallback caso o seletor falhe por algum motivo
                const todos = document.querySelectorAll('input[type="checkbox"]');
                for (let c of todos) {
                    if (c.checked) { check = c; break; }
                }
            }
            
            if (!check) { 
                alert("Selecione um item no histórico antes de clicar em Exibir."); 
                return; 
            }
            
            try {
                const res = await fetch(`/historico_panorama/${check.value}`);
                if (!res.ok) throw new Error("Erro HTTP " + res.status);
                
                const data = await res.json();
                if (data.erro) { alert("Erro no servidor: " + data.erro); return; }
                
                console.log("Retorno do historico:", data);
                aplicarValores(data); 
                window.scrollTo(0, 0);
            } catch(e) {
                console.error("Falha no exibir:", e);
                alert("Erro ao carregar o histórico. Verifique o Console (F12).");
            }
        }

        async function excluirSelecionado() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico."); return; }
            if (!confirm("Excluir este item do histórico?")) return;
            
            try {
                await fetch(`/excluir_panorama/${check.value}`, { method: 'DELETE' });
                carregarHistorico();
            } catch(e) {
                alert("Erro ao excluir.");
            }
        }

        function gerarPDFPanorama() {
            const check = document.querySelector('.check-historico:checked');
            if (!check) { alert("Selecione um item no histórico para gerar o PDF."); return; }
            window.open(`/gerar_pdf_panorama/${check.value}`, '_blank');
        }

        // ===== LIGANDO OS BOTOES =====
        document.addEventListener("DOMContentLoaded", () => {
            document.getElementById('btn-verificar').addEventListener('click', carregarPanorama);
            document.getElementById('btn-salvar').addEventListener('click', salvarPanorama);
            document.getElementById('btn-exibir').addEventListener('click', exibirSelecionado);
            document.getElementById('btn-excluir').addEventListener('click', excluirSelecionado);
            document.getElementById('btn-pdf').addEventListener('click', gerarPDFPanorama);

            carregarHistorico();
        });
"""

# Substitui o bloco de script inteiro
scripts = list(re.finditer(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE))
for m in reversed(scripts):
    if 'carregarPanorama' in m.group(1):
        html = html[:m.start(1)] + novo_js + html[m.end(1):]
        break

with open(arquivo, "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Frontend blindado. O botao Exibir agora tem fallback duplo e log de erro.")
print("\n=== PROXIMO PASSO ===")
print("1. NAO precisa reiniciar o servidor (apenas frontend mudou).")
print("2. Va no navegador: http://127.0.0.1:9994/panorama")
print("3. Aperte Ctrl + Shift + R.")
print("4. Marque um item no historico e clique em Exibir.")
