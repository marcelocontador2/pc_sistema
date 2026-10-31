from pathlib import Path

arquivo = Path("pc_frontend/custo_pessoal.html")
conteudo = arquivo.read_text(encoding="utf-8")

# 1. Adicionar type="button" nos botoes de entidade
conteudo = conteudo.replace(
    '<button id="btn-cofen" class="btn-entidade ativo" onclick="mudarEntidade(\'COFEN\')"',
    '<button type="button" id="btn-cofen" class="btn-entidade ativo" onclick="mudarEntidade(\'COFEN\')"'
)

conteudo = conteudo.replace(
    '<button id="btn-coren" class="btn-entidade" onclick="mudarEntidade(\'COREN\')"',
    '<button type="button" id="btn-coren" class="btn-entidade" onclick="mudarEntidade(\'COREN\')"'
)

# 2. Adicionar type="button" em TODOS os botoes que nao tem (para evitar submit acidental)
import re
# Encontrar todos os <button ...> sem type
def add_type(match):
    btn = match.group(0)
    if 'type=' not in btn:
        return btn.replace('<button ', '<button type="button" ', 1)
    return btn

conteudo = re.sub(r'<button[^>]*>', add_type, conteudo)

arquivo.write_text(conteudo, encoding="utf-8")
print("OK: type=\"button\" adicionado em todos os botoes!")
print("OK: Botoes nao vao mais recarregar a pagina ao clicar.")
