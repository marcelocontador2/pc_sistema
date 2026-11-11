import re
import shutil
from datetime import datetime

ARQ = r"pc_frontend\notas_explicativas.html"
backup = f"pc_frontend/notas_explicativas.html.bak_decl_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(ARQ, backup)
print(f"[OK] Backup: {backup}")

with open(ARQ, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substitui o bloco antigo da declaração por um mais elegante
padrao_decl = r'<div id="declaracao-conformidade".*?</div>\s*</div>'
nova_decl = """
<div id="declaracao-conformidade" style="margin-top: 50px; padding: 30px; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); page-break-inside: avoid;">
    <h3 style="color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; margin-top: 0; margin-bottom: 20px; font-size: 14px;">Declaração de Conformidade</h3>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;">Declaramos, na qualidade de responsáveis pela gestão e pela elaboração das demonstrações contábeis consolidadas do Conselho Federal de Enfermagem (COFEN), referentes ao período de 01/01/2026 a 30/09/2026 (2026-TRIMESTRE-3), que:</p>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;"><b>1.</b> As informações contábeis foram elaboradas em conformidade com as disposições da Lei nº 4.320/1964, as diretrizes do Manual de Contabilidade Aplicada ao Setor Público (MCASP) e as Normas Brasileiras de Contabilidade Técnicas do Setor Público (NBC TSP).</p>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;"><b>2.</b> As demonstrações contábeis consolidadas (Balanço Patrimonial, Balanço Orçamentário, Balanço Financeiro, Demonstração das Variações Patrimoniais, Demonstração dos Fluxos de Caixa e Demonstração das Mutações do Patrimônio Líquido) refletem, de forma fidedigna, a posição patrimonial e financeira do COFEN e o desempenho da execução orçamentária no período.</p>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;"><b>3.</b> Os registros contábeis estão amparados em documentação de suporte idônea e devidamente auditada internamente, observando os princípios da legalidade, da transparência, da economicidade e da segregação de funções.</p>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;"><b>4.</b> As práticas de gestão de riscos, os controles internos administrativos e o processo de conformidade foram implementados e mantidos operantes durante todo o período analisado, garantindo a integridade dos dados apresentados.</p>
    
    <p style="text-align: justify; line-height: 1.6; font-size: 11px; margin-bottom: 12px;"><b>5.</b> Esta declaração é firmada com base nas informações extraídas dos sistemas corporativos e validadas pelos responsáveis técnicos, nos termos da Resolução COFEN nº 764/2024 (Prestação de Contas).</p>
    
    <div style="margin-top: 40px; text-align: center; border-top: 1px dashed #ccc; padding-top: 25px;">
        <p style="margin: 0; font-size: 13px; font-weight: bold; color: #003366;" id="nome-contador">Marcelo Ribeiro Medeiros</p>
        <p style="margin: 5px 0 0 0; font-size: 11px; color: #555;">CRC: <span id="crc-contador">RJ-066005/O-8T</span></p>
        <p style="margin: 5px 0 0 0; font-size: 11px; color: #555;">CPF: <span id="cpf-contador">***.212.***-**</span></p>
    </div>
</div>
"""

if re.search(padrao_decl, html, re.DOTALL):
    html = re.sub(padrao_decl, nova_decl, html, flags=re.DOTALL)
    print("[OK] Declaração redesenhada.")
else:
    # Se não encontrou o bloco antigo, adiciona antes do </body>
    if 'declaracao-conformidade' not in html:
        html = html.replace('</body>', nova_decl + '</body>')
    else:
        print("[AVISO] Bloco de declaração encontrado, mas regex não casou. Verifique manualmente.")

# 2. Corrige o JavaScript para aplicar a máscara LGPD no CPF
funcao_antiga = """        if (data.contador_cpf) document.getElementById('cpf-contador').innerText = data.contador_cpf;"""
funcao_nova = """        if (data.contador_cpf) {
            let cpf = data.contador_cpf.replace(/[^0-9]/g, '');
            let cpfFormatado = cpf;
            if (cpf.length === 11) {
                cpfFormatado = '***.' + cpf.substring(3,6) + '.***-**';
            }
            document.getElementById('cpf-contador').innerText = cpfFormatado;
        }"""

if funcao_antiga in html:
    html = html.replace(funcao_antiga, funcao_nova)
    print("[OK] Máscara LGPD aplicada ao CPF.")
else:
    print("[AVISO] Linha de CPF não encontrada no JavaScript.")

with open(ARQ, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] Template atualizado.")
