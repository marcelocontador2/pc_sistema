import re

path = "composicao_receitas_despesas.html"
with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# 1. Remove qualquer referencia antiga a gerarPDF() ou gerarPDFHistorico() que possa estar quebrada
s = re.sub(r'function\s+gerarPDFHistorico\(\)\s*\{.*?\n\}', '', s, flags=re.DOTALL)

# 2. Cria a funcao gerarPDFHistorico correta
nova_funcao = '''
function gerarPDFHistorico() {
    const check = document.querySelector('.check-hist:checked');
    if (!check) { 
        alert("Selecione um item no histórico para gerar o PDF."); 
        return; 
    }
    // Abre a rota de PDF em uma nova aba (o backend vai gerar e devolver o arquivo)
    window.open('/gerar_pdf_composicao_receitas_despesas/' + check.value, '_blank');
}
'''

# 3. Injeta a funcao antes do </script>
if "function gerarPDFHistorico()" not in s:
    s = s.replace("</script>", nova_funcao + "\n</script>")
    print("OK: Funcao gerarPDFHistorico() injetada com sucesso!")
else:
    print("AVISO: A funcao gerarPDFHistorico ja existia no arquivo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
