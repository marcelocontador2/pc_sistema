c = open('main.py', encoding='utf-8-sig').read()

# Remove o resquício de dados simulados que ficou após o return
trecho_antigo = '''        return {"erro": True, "mensagem": str(e)},
            {"nome": "Enfermagem", "valor": 300000.00},
            {"nome": "Tecnologia da InformaÃ§Ã£o", "valor": 200000.00},
            {"nome": "Recursos Humanos", "valor": 100000.00}
        ]
    }'''

trecho_novo = '''        return {"erro": True, "mensagem": str(e)}'''

if trecho_antigo in c:
    c = c.replace(trecho_antigo, trecho_novo)
    print("[OK] Resquício removido com sucesso!")
else:
    # Tenta uma versão mais flexível (pode ter acentos diferentes)
    import re
    padrao = r'return \{"erro": True, "mensagem": str\(e\)\},.*?\n\s*\}'
    if re.search(padrao, c, re.DOTALL):
        c = re.sub(padrao, 'return {"erro": True, "mensagem": str(e)}', c, flags=re.DOTALL)
        print("[OK] Resquício removido via regex!")
    else:
        print("[AVISO] Resquício não encontrado. Tentando remoção manual...")
        # Remove tudo depois do return até o próximo @app
        pos_return = c.find('return {"erro": True, "mensagem": str(e)}')
        if pos_return != -1:
            # Encontra o próximo @app após o return
            pos_proximo_app = c.find('@app.get', pos_return)
            if pos_proximo_app != -1:
                c = c[:pos_return + len('return {"erro": True, "mensagem": str(e)}')] + '\n\n' + c[pos_proximo_app:]
                print("[OK] Remoção manual realizada!")

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py atualizado!")
