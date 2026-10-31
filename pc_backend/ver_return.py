c = open('main.py', encoding='utf-8-sig').read()
start = c.find('async def api_custo_pessoal')
if start != -1:
    end = c.find('"rcl_atual"', start)
    if end != -1:
        inicio_return = c.rfind('return {', start, end)
        if inicio_return != -1:
            print('=== INÍCIO DO RETURN CORRETO ===')
            print(c[inicio_return:inicio_return+2000])
            print('=== FIM DO RETURN ===')
        else:
            print('Return nao encontrado.')
    else:
        print('Chave rcl_atual nao encontrada.')
