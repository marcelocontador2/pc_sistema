import shutil, datetime

# Backup
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2("analise_comparativo_despesas.html", f"analise_comparativo_despesas.html.bak_{ts}")

c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

idx_inicio = c.find('async function verificar()')

if idx_inicio == -1:
    print("[ERRO] Função 'async function verificar()' não encontrada no HTML.")
else:
    # Encontra a abertura da chave '{'
    idx_chave = c.find('{', idx_inicio)
    
    # Conta as chaves para achar o fechamento da função
    nivel = 1
    i = idx_chave + 1
    while nivel > 0 and i < len(c):
        if c[i] == '{': nivel += 1
        elif c[i] == '}': nivel -= 1
        i += 1
    
    # i agora aponta para o caractere logo após a chave de fechamento '}'
    
    nova_funcao = """async function verificar() {
    console.log("=== INICIANDO VERIFICAR ===");
    
    // Pega todos os selects da tela para garantir que não falhe
    const selects = Array.from(document.querySelectorAll('select'));
    
    // Tenta achar os selects pelo ID, Nome ou pela ordem (0, 1, 2)
    const elAno = selects.find(s => (s.id && s.id.toLowerCase().includes('ano')) || (s.name && s.name.toLowerCase().includes('ano'))) || selects[0];
    const elTipo = selects.find(s => (s.id && (s.id.toLowerCase().includes('tipo') || s.id.toLowerCase().includes('periodo'))) || (s.name && s.name.toLowerCase().includes('tipo'))) || selects[1];
    const elValor = selects.find(s => (s.id && (s.id.toLowerCase().includes('valor') || s.id.toLowerCase().includes('trimestre') || s.id.toLowerCase().includes('mes'))) || (s.name && (s.name.toLowerCase().includes('valor') || s.name.toLowerCase().includes('trimestre')))) || selects[2];

    if (!elAno || !elTipo || !elValor) {
        console.error("ERRO: Selects não encontrados na tela", selects);
        alert("Erro: Campos de período não encontrados.");
        return;
    }

    const periodoAtual = `${elAno.value}-${elTipo.value}-${elValor.value}`;
    console.log("Período selecionado:", periodoAtual);

    try {
        const res = await fetch(`/api/comparativo_despesas_v2/${periodoAtual}?_t=${Date.now()}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const data = await res.json();
        console.log("[DEBUG] Dados recebidos da API:", data);

        if (data.erro) {
            alert("Erro da API: " + data.mensagem);
            return;
        }

        atualizarCards(data);
        renderizarTabela(data);
        console.log("Cards e tabela atualizados com sucesso!");
    } catch (e) {
        console.error("[ERRO JS]", e);
        alert("Falha ao carregar os dados: " + e.message);
    }
}"""
    
    # Substitui o bloco antigo inteiro pela nova função
    c = c[:idx_inicio] + nova_funcao + c[i:]
    open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
    print("[OK] Função verificar() substituída inteiramente com sucesso!")
