import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
main_path = r"pc_frontend\analise_centro_custos.html"

shutil.copy2(main_path, f"{main_path}.bak_limpeza_painel_{ts}")
c = open(main_path, encoding='utf-8').read()

# 1. Remove o PAINEL LATERAL (o que está aparecendo no print)
c = re.sub(r'<!-- PAINEL DE CONCLUSÃO EDITÁVEL -->.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<div id="painel-conclusao".*?</div>\s*</div>\s*</div>\s*</div>\s*', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-painel-conclusao">.*?</script>', '', c, flags=re.DOTALL)

# 2. Remove qualquer modal/script antigo
c = re.sub(r'<div id="modal-conclusao".*?</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*', '', c, flags=re.DOTALL)
c = re.sub(r'<script id="js-modal-conclusao">.*?</script>', '', c, flags=re.DOTALL)
c = re.sub(r'<button[^>]*id="btn-editar-conclusao".*?</button>', '', c, flags=re.DOTALL)

# 3. Adiciona o botão ao lado do Gerar PDF
btn_edit = ' <button id="btn-editar-conclusao" style="background: #f59e0b; color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-left: 10px;">✏️ Editar Conclusão</button>'

# Procura o botão Gerar PDF e insere depois
match = re.search(r'(<button[^>]*>Gerar PDF</button>)', c, re.IGNORECASE)
if match:
    c = c.replace(match.group(1), match.group(1) + btn_edit, 1)
    print("[OK] Botão 'Editar Conclusão' adicionado ao lado de 'Gerar PDF'")

# 4. Adiciona o MODAL simples com 4 blocos editáveis
modal = """
<div id="modal-conclusao" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 99999; justify-content: center; align-items: center; padding: 20px;">
    <div style="background: white; padding: 25px; border-radius: 12px; width: 1000px; max-width: 98%; max-height: 92vh; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
        
        <h3 style="margin: 0 0 10px 0; color: #1a202c;">✏️ Editar Conclusão do Relatório</h3>
        <p style="color: #718096; font-size: 13px; margin: 0 0 15px 0;">Edite os textos abaixo. As alterações refletirão no próximo PDF.</p>
        
        <div style="overflow-y: auto; flex: 1;">
            <label style="display: block; margin-top: 15px; font-weight: bold; font-size: 14px;">1. Conclusão sobre o Total Executado</label>
            <div id="edit-conclusao-total" contenteditable="true" style="min-height: 80px; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>
            
            <label style="display: block; margin-top: 15px; font-weight: bold; font-size: 14px;">2. Análise de Concentração</label>
            <div id="edit-conclusao-concentracao" contenteditable="true" style="min-height: 80px; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>
            
            <label style="display: block; margin-top: 15px; font-weight: bold; font-size: 14px;">3. Alertas e Pontos de Atenção</label>
            <div id="edit-conclusao-alertas" contenteditable="true" style="min-height: 80px; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>
            
            <label style="display: block; margin-top: 15px; font-weight: bold; font-size: 14px;">4. Recomendações</label>
            <div id="edit-conclusao-recomendacoes" contenteditable="true" style="min-height: 80px; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 14px; margin-top: 5px; background: #fff; line-height: 1.6;"></div>
        </div>
        
        <div style="margin-top: 15px; display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
            <button id="btn-cancelar-conclusao" style="padding: 10px 20px; border: none; border-radius: 6px; background: #e2e8f0; color: #4a5568; font-weight: bold; cursor: pointer;">Cancelar</button>
            <button id="btn-salvar-conclusao-modal" style="padding: 10px 20px; border: none; border-radius: 6px; background: #38a169; color: white; font-weight: bold; cursor: pointer;">💾 Salvar Conclusão</button>
        </div>
    </div>
</div>

<script id="js-modal-conclusao">
document.addEventListener('DOMContentLoaded', function() {
    const btnAbrir = document.getElementById('btn-editar-conclusao');
    const modal = document.getElementById('modal-conclusao');
    const btnCancelar = document.getElementById('btn-cancelar-conclusao');
    const btnSalvar = document.getElementById('btn-salvar-conclusao-modal');
    
    const campos = {
        'conclusao-total': document.getElementById('edit-conclusao-total'),
        'conclusao-concentracao': document.getElementById('edit-conclusao-concentracao'),
        'conclusao-alertas': document.getElementById('edit-conclusao-alertas'),
        'conclusao-recomendacoes': document.getElementById('edit-conclusao-recomendacoes')
    };
    
    window.htmlOriginal = {};
    
    btnAbrir.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) {
            alert("Atenção: Selecione um item no Histórico Salvo antes de editar.");
            return;
        }
        
        const id = check.value;
        modal.style.display = 'flex';
        window.htmlOriginal = {};
        
        for (const campo of Object.values(campos)) {
            campo.innerHTML = '<em style="color:#999;">Carregando...</em>';
        }
        
        try {
            const res = await fetch(`/historico_centro_custos/${id}`);
            const data = await res.json();
            const dados = data.dados ? data.dados : data;
            
            let textoSalvo = null;
            if (dados.conclusao_personalizada) {
                try {
                    textoSalvo = typeof dados.conclusao_personalizada === 'string' 
                        ? JSON.parse(dados.conclusao_personalizada) 
                        : dados.conclusao_personalizada;
                } catch(e) {}
            }
            
            if (textoSalvo && Object.keys(textoSalvo).length > 0 && !textoSalvo.blocos) {
                for (const [chave, campo] of Object.entries(campos)) {
                    if (textoSalvo[chave]) {
                        campo.innerHTML = textoSalvo[chave];
                        window.htmlOriginal[chave] = textoSalvo[chave];
                    } else {
                        campo.innerHTML = '';
                        window.htmlOriginal[chave] = '';
                    }
                }
            } else {
                await extrairDoRelatorio(id);
            }
        } catch(e) {
            console.error(e);
            alert("Erro ao carregar os textos.");
        }
    });
    
    function extrairDoRelatorio(historicoId) {
        return new Promise((resolve) => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = `/relatorio_centro_custos?historico_id=${historicoId}&_t=${Date.now()}`;
            document.body.appendChild(iframe);
            
            setTimeout(() => {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    for (const [chave, campo] of Object.entries(campos)) {
                        const el = doc.getElementById(chave);
                        if (el) {
                            campo.innerHTML = el.innerHTML;
                            window.htmlOriginal[chave] = el.innerHTML;
                        } else {
                            campo.innerHTML = '';
                            window.htmlOriginal[chave] = '';
                        }
                    }
                } catch(e) { console.error(e); }
                document.body.removeChild(iframe);
                resolve();
            }, 4000);
        });
    }
    
    btnCancelar.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    btnSalvar.addEventListener('click', async function() {
        const check = document.querySelector('.check-historico:checked');
        if (!check) return;
        
        const id = check.value;
        const htmlEditado = {};
        
        for (const [chave, campo] of Object.entries(campos)) {
            const htmlAtual = campo.innerHTML.trim();
            const htmlOriginal = (window.htmlOriginal[chave] || '').trim();
            const textoAtual = campo.innerText.trim();
            
            if (!textoAtual) {
                htmlEditado[chave] = htmlOriginal;
            } else if (htmlAtual === htmlOriginal) {
                htmlEditado[chave] = htmlOriginal;
            } else {
                htmlEditado[chave] = htmlAtual;
            }
        }
        
        btnSalvar.innerText = "Salvando...";
        btnSalvar.disabled = true;
        
        try {
            const res = await fetch(`/salvar_conclusao_centro_custos/${id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ texto: JSON.stringify(htmlEditado) })
            });
            const data = await res.json();
            
            if (data.erro) {
                alert("Erro: " + data.mensagem);
            } else {
                alert("Conclusão salva com sucesso! Agora clique em 'Gerar PDF'.");
                modal.style.display = 'none';
            }
        } catch(e) {
            alert("Erro de conexão.");
        } finally {
            btnSalvar.innerText = "💾 Salvar Conclusão";
            btnSalvar.disabled = false;
        }
    });
});
</script>
"""

c = c.replace('</body>', modal + '\n</body>', 1)
open(main_path, 'w', encoding='utf-8').write(c)
print("[OK] Painel lateral REMOVIDO!")
print("[OK] Botao 'Editar Conclusao' ao lado do 'Gerar PDF'!")
print("[OK] Modal com 4 blocos editaveis restaurado!")
