import re

c = open('analise_comparativo_despesas.html', encoding='utf-8-sig').read()

# Trecho antigo que falhou
trecho_antigo = r'const elAno = document\.querySelector\(\x27select#ano\x27\).*?const periodoAtual = `\$\{elAno\.value\}-\$\{elTipo\.value\}-\$\{elValor\.value\}`;'

# Novo trecho com fallback para pegar qualquer select na tela
trecho_novo = '''const selects = document.querySelectorAll('select');
                const elAno = document.getElementById('ano') || document.querySelector('[name="ano"]') || document.querySelector('select[id*="ano"]') || selects[0];
                const elTipo = document.getElementById('tipo') || document.querySelector('[name="tipo"]') || document.querySelector('select[id*="tipo"]') || selects[1];
                const elValor = document.getElementById('valor') || document.querySelector('[name="valor"]') || document.querySelector('select[id*="valor"]') || document.querySelector('select[id*="trimestre"]') || selects[2];
                
                if (!elAno || !elTipo || !elValor) {
                    console.error("ERRO: Selects não encontrados!", { elAno, elTipo, elValor, totalSelects: selects.length });
                    alert("Erro: IDs dos selects não encontrados.");
                    return;
                }
                
                const periodoAtual = `${elAno.value}-${elTipo.value}-${elValor.value}`;'''

c = re.sub(trecho_antigo, trecho_novo, c, flags=re.DOTALL)

# Se o regex anterior não pegou (por diferença de aspas), tenta outro padrão mais amplo
if trecho_novo not in c:
    c = re.sub(r'const elAno = document\.querySelector\(.*?const periodoAtual = `\$\{elAno\.value\}-\$\{elTipo\.value\}-\$\{elValor\.value\}`;', trecho_novo, c, flags=re.DOTALL)

open('analise_comparativo_despesas.html', 'w', encoding='utf-8').write(c)
print("[OK] Leitura dos selects corrigida com fallback!")
