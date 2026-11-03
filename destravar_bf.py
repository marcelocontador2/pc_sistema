import re, shutil, datetime

ts = datetime.datetime.now().strftime('%H%M%S')
arquivo = r"pc_frontend\analise_financeira_bf.html"

shutil.copy2(arquivo, f"{arquivo}.bak_travado_{ts}")
c = open(arquivo, encoding='utf-8').read()

# 1. Limpa qualquer lixo da função anterior que possa ter quebrado o script
c = re.sub(r'function gerarPDFHistorico\(\) \{.*?\n        \}', '', c, flags=re.DOTALL)

# 2. Limpa qualquer botão que esteja chamando funções antigas
# Procura botões que tenham a palavra "PDF" e força o onclick correto
c = re.sub(r'<button([^>]*)>(.*?Gerar PDF.*?)</button>', r'<button\1 onclick="gerarPDFFinanceiro()">\2</button>', c, flags=re.IGNORECASE)

# 3. Injeta a função perfeita no final do script
nova_funcao = """
        function gerarPDFFinanceiro() {
            console.log("Botão clicado! Verificando histórico...");
            const sel = document.querySelector('input[name="historico"]:checked') || document.querySelector('input[type="radio"]:checked');
            
            if (!sel) {
                alert("Atenção: Selecione um item do Histórico Salvo antes de gerar o PDF.");
                return;
            }
            
            const url = `/gerar_pdf_analise_financeira_bf?historico_id=${sel.value}`;
            console.log("Abrindo URL:", url);
            
            // Técnica à prova de bloqueador de pop-up
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
"""

if '</script>' in c:
    c = c.replace('</script>', nova_funcao + '\n    </script>', 1)
else:
    c += f"<script>{nova_funcao}</script>"

open(arquivo, 'w', encoding='utf-8').write(c)
print("[OK] Botão de PDF da Análise Financeira destravado e reescrito!")
