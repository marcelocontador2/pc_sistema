import re

c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# Padrão para encontrar a função desativarOutrosPeriodos (que está incompleta)
padrao = r'function desativarOutrosPeriodos\(origem\) \{.*?\n\}'

# Função completa e correta
nova_funcao = '''function desativarOutrosPeriodos(origem) {
    const selectMes = document.getElementById('upload-mes');
    const selectTrimestre = document.getElementById('upload-trimestre');
    const selectExercicio = document.getElementById('upload-exercicio');
    
    if (origem === 'mes' && selectMes.value !== '') {
        selectTrimestre.disabled = true;
        selectExercicio.disabled = true;
    } else if (origem === 'trimestre' && selectTrimestre.value !== '') {
        selectMes.disabled = true;
        selectExercicio.disabled = true;
    } else if (origem === 'exercicio' && selectExercicio.value !== '') {
        selectMes.disabled = true;
        selectTrimestre.disabled = true;
    } else {
        selectMes.disabled = false;
        selectTrimestre.disabled = false;
        selectExercicio.disabled = false;
    }
}'''

# Substitui a função antiga
if re.search(padrao, c, re.DOTALL):
    c = re.sub(padrao, nova_funcao, c, flags=re.DOTALL)
    print("[OK] Função desativarOutrosPeriodos corrigida!")
else:
    print("[AVISO] Função desativarOutrosPeriodos não encontrada. Tentando outra abordagem...")
    # Tenta substituir pela versão que está no HTML
    c = c.replace('else { selectMes.disabled = false; selectTrimestre.disabled = false; selectExercicio.disabled = ', 'else { selectMes.disabled = false; selectTrimestre.disabled = false; selectExercicio.disabled = false; }')

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] index.html atualizado!")
