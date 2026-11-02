import re

c = open('main.py', encoding='utf-8-sig').read()

# Remove o resquício ", "media_mensal": 0}" que está sobrando
c = c.replace('    }, "media_mensal": 0}', '    }')

# Verifica se o return do bloco if anterior está correto
# A estrutura deve ser: return { ... } (sem nada depois do })
padrao_antigo = r'return \{\s*"periodo_atual": periodo_atual,\s*"periodo_anterior": None,\s*"atual": atual,\s*"anterior": \{.*?\},\s*"variacao_total": 0,\s*"variacao_pct": 0,\s*"aviso": "Não há dados para o período anterior."\s*\}\s*\}, "media_mensal": 0\}'

if re.search(padrao_antigo, c, re.DOTALL):
    # Substitui o bloco quebrado pelo correto
    c = re.sub(padrao_antigo, 
               '''return {
            "periodo_atual": periodo_atual,
            "periodo_anterior": None,
            "atual": atual,
            "anterior": {"total": 0, "centros": [], "maior_centro": {"nome": "-", "valor": 0}, "media_mensal": 0, "meses": {}},
            "variacao_total": 0,
            "variacao_pct": 0,
            "aviso": "Não há dados para o período anterior."
        }''', c, flags=re.DOTALL)
    print("[OK] Bloco do if anterior corrigido!")
else:
    print("[AVISO] Padrão não encontrado. Tentando substituição manual...")
    # Tenta substituir a linha problemática diretamente
    c = c.replace('    }, "media_mensal": 0}', '    }')

open('main.py', 'w', encoding='utf-8').write(c)
print("[OK] main.py corrigido!")
