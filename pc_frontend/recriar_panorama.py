import re
import shutil

path = "panorama.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

shutil.copy(path, path + ".bak_recriar_panorama")

# 1. Remove TODOS os scripts antigos (para limpar a bagunça)
s = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.DOTALL | re.IGNORECASE)

# 2. Cria o script limpo com todas as funções
novo_js = '''
<script>
let dadosAtuais = null;

async function carregarHistorico() {
    try {
        const r = await fetch('/historico_panorama');
        const data = await r.json();
        const lista = document.getElementById('historico-lista');
        if (!lista) return;
        if (!data || data.length === 0) { lista.innerHTML = '<li>Nenhum histórico.</li>'; return; }
        let html = '';
        data.forEach(item => {
            html += `<li><label><input type="checkbox" class="check-hist" value="${item.id}" style="margin-right:5px;"><strong>${item.periodo}</strong><br><small style="color:#666;">${item.data_geracao}</small></label></li>`;
        });
        lista.innerHTML = html;
    } catch (e) { 
        console.error(e); 
        const lista = document.getElementById('historico-lista');
        if(lista) lista.innerHTML = '<li>Erro ao carregar.</li>';
    }
}

async function carregarPanorama() {
    const ano = document.getElementById('ano').value;
    const tipo = document.getElementById('tipo_periodo').value;
    const valor = document.getElementById('trimestre').value;
    const periodo = `${ano}-${tipo}-${valor}`;
    
    document.getElementById('periodo-titulo').innerText = `Resultados Gerais — ${valor}º Trimestre de ${ano}`;
    
    try {
        const response = await fetch(`/api/panorama/${periodo}`);
        
        // Tratamento do 404 (dados ausentes)
        if (response.status === 404) {
            alert("Aviso: Não há demonstrativos importados para o período " + periodo + ". Verifique se os relatórios foram enviados.");
            preencherCards({}); // Limpa os cards
            return;
        }
        
        if (!response.ok) throw new Error("Erro HTTP " + response.status);
        
        const data = await response.json();
        
        if (data.erro) { 
            alert("Aviso: " + (data.mensagem || "Faltam demonstrativos importados.")); 
            preencherCards({}); 
            return; 
        }
        
        // Verifica se os valores estão zerados
        const valores = Object.values(data).filter(v => typeof v === 'number');
        const todosZerados = valores.length > 0 && valores.every(v => v === 0);
        
        if (todosZerados || valores.length === 0) {
            alert("Aviso: Não há demonstrativos importados para o período " + periodo + ".");
            preencherCards({});
            return;
        }
        
        dadosAtuais = data;
        preencherCards(data);
        
        const btnSalvar = document.getElementById("btn-salvar");
        if(btnSalvar) {
            btnSalvar.setAttribute("data-periodo", periodo);
            btnSalvar.style.display = "inline-block";
            btnSalvar.innerText = "Confirmar e Salvar";
            btnSalvar.disabled = false;
        }
    } catch (e) { 
        console.error(e); 
        alert("Erro de conexão ao buscar panorama.");
    }
}

async function salvarPanorama() {
    const btn = document.getElementById("btn-salvar");
    const periodo = btn.getAttribute("data-periodo");
    if (!periodo) { alert("Verifique o panorama antes de salvar."); return; }
    if (!dadosAtuais) { alert("Erro: Nenhum dado na memória."); return; }
    
    btn.innerText = "Salvando..."; 
    btn.disabled = true;
    
    try {
        const res = await fetch("/salvar_panorama/" + periodo, { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dadosAtuais)
        });
        const data = await res.json();
        if (data.ok) {
            alert("Resultados salvos com sucesso!");
            carregarHistorico();
        } else {
            alert("Erro: " + data.mensagem);
        }
    } catch (e) {
        alert("Erro de conexão ao salvar.");
    } finally {
        btn.innerText = "Confirmar e Salvar"; 
        btn.disabled = false;
    }
}

async function exibirSelecionado() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { alert("Selecione um item no histórico."); return; }
    try {
        const r = await fetch('/historico_panorama/' + check.value);
        if (!r.ok) throw new Error("HTTP " + r.status);
        const dados = await r.json();
        preencherCards(dados);
    } catch (e) {
        alert("Erro ao carregar histórico: " + e.message);
    }
}

// Função de preenchimento dos cards (mantida genérica, adapte se necessário)
function preencherCards(data) {
    const mapa = {
        'caixa': 'card-caixa',
        'ativo_total': 'card-ativo',
        'passivo_total': 'card-passivo',
        'patrimonio_liquido': 'card-pl',
        'receitas': 'card-receitas',
        'despesas': 'card-despesas',
        'superavit': 'card-superavit',
        'superavit_patrimonial': 'card-superavit-patrimonial',
        'superavit_financeiro': 'card-superavit-financeiro'
    };
    // Se os cards tiverem IDs específicos, faça o mapeamento. 
    // Como não sabemos os IDs exatos, deixamos um fallback visual.
    // O usuário pode adaptar os IDs conforme necessário.
    for (const [chave, id] of Object.entries(mapa)) {
        const el = document.getElementById(id);
        if (el) {
            const v = data[chave] || 0;
            el.innerText = "R$ " + (v / 1000000).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " mi";
        }
    }
}

document.addEventListener("DOMContentLoaded", function() {
    carregarHistorico();
    
    // Vincula os botões
    const btnExibir = document.querySelector('button[onclick*="exibirSelecionado"]') || document.getElementById('btn-exibir');
    if (btnExibir) {
        btnExibir.removeAttribute('onclick');
        btnExibir.addEventListener('click', exibirSelecionado);
    }
    
    const btnSalvar = document.querySelector('button[onclick*="salvarPanorama"]') || document.getElementById('btn-salvar');
    if (btnSalvar) {
        btnSalvar.removeAttribute('onclick');
        btnSalvar.addEventListener('click', salvarPanorama);
    }
});
</script>
'''

# 3. Injeta o novo script antes do </body>
if "</body>" in s:
    s = s.replace("</body>", novo_js + "\n</body>")
else:
    s += novo_js

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK: Panorama.html recriado com JavaScript limpo e funcoes essenciais!")
