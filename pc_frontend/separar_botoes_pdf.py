p = 'notas_explicativas.html'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Restaura o botão da aba Tradicional para chamar a rota antiga (se ele tiver sido alterado)
# Procura qualquer botão de PDF que esteja chamando a rota do MCASP e volta para a Tradicional
s = s.replace("window.open('/gerar_pdf_notas_mcasp", "window.open('/gerar_pdf_notas/")
s = s.replace('window.open("/gerar_pdf_notas_mcasp', 'window.open("/gerar_pdf_notas/')

# 2. Adiciona um NOVO botão na aba MCASP, se ele não existir
if 'baixarPDFMCASP' not in s:
    # Botão novo para a aba MCASP
    botao_mcasp = '''<button onclick="baixarPDFMCASP()" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 20px; margin-left: 10px;">📄 Gerar PDF MCASP</button>'''
    
    # Procura o botão de salvar do MCASP e coloca o botão de PDF ao lado
    if 'salvarMCASP()' in s:
        s = s.replace('salvarMCASP()" style="padding: 10px 20px; background: #28a745;', 
                      'salvarMCASP()" style="padding: 10px 20px; background: #28a745;')
        s = s.replace('💾 Salvar Alterações MCASP</button>', 
                      '💾 Salvar Alterações MCASP</button>' + botao_mcasp)
    
    # Adiciona a função JavaScript
    js_mcasp = """
<script>
    function baixarPDFMCASP() {
        const periodo = '2026-TRIMESTRE-3';
        window.open('/gerar_pdf_notas_mcasp?periodo=' + periodo, '_blank');
    }
</script>
"""
    if '</body>' in s:
        s = s.replace('</body>', js_mcasp + '\n</body>')
    else:
        s += js_mcasp

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print("OK: Botoes de PDF separados no frontend!")
