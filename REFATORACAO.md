# Refatoracao do main.py - Resultado Final

## Resultado

| Metrica | Inicio | Final | Reducao |
|---|---|---|---|
| Linhas | 12.141 | 9.003 | -3.138 (-25,8%) |
| Rotas (app.routes) | 313 | 215 | -98 (-31,3%) |
| Paths GET 200 | 74 | 74 | 0 regressoes |
| Duplicatas reais | 25 | 0 | -25 |

## PRs executados: ~35 (#1 a #3ah)

Cada PR: backup (pre_PR*) + corte cirurgico + validacao de import + validacao de comportamento.

## Tipos de duplicata resolvidos

1. Blocos inteiros (A e B) - copias literais de ~1.500 linhas
2. Funcoes duplicadas - mesmo nome, implementacoes iguais
3. Funcoes divergentes - mesmo nome, implementacoes diferentes (mantida a ativa)
4. Decorators orfaos - @app.get sem def abaixo, decorando funcoes erradas

## O que resta (NAO e codigo morto)

14 funcoes com "mesmo nome" em escopos diferentes - sao helpers locais dentro de funcoes maiores, com propositos diferentes. NAO sao duplicatas globais. Apagar quebraria as funcoes que as usam.

Exemplos:
- calc_var: v1 retorna string formatada, v2 retorna numero
- fmt: 7 definicoes locais, cada uma no escopo da funcao que a usa
- pct, limpar, buscar, ler_csv: idem

## Causa raiz das duplicatas

58 scripts fix_* usaram o padrao perigoso:

    idx = conteudo.find('ancora')        # acha a PRIMEIRA ocorrencia
    fim = conteudo.find('\n', idx)
    conteudo = conteudo[:idx] + bloco_novo + conteudo[fim:]

Por que duplica:
1. find() cego - se a ancora aparece 2+ vezes, so a primeira e substituida
2. O bloco_novo frequentemente contem funcoes auxiliares (calc_var, fmt) que ja existiam
3. Sem verificacao de duplicata antes de escrever

## Regras para prevenir recorrencia

1. NUNCA rodar scripts fix_*.py no main.py. Editar via IDE com diff, ou via PR.
2. NUNCA usar find() sem verificar conteudo.count(ancora) == 1.
3. NUNCA inserir bloco com funcoes embutidas - helpers em modulo separado.
4. Apos qualquer edicao: contar FunctionDef por nome via AST. Se nome aparece 2x no mesmo escopo, abortar.

## Backups disponiveis

- main.py.bak_20261116_1238 - ORIGINAL (580,7 KB, 12.141 linhas)
- main.py.pre_PR* - 35 backups, um por PR
- baseline_rotas.json - 81 paths, 74 com 200 (estado original)

Para reverter qualquer PR: Copy-Item "pc_backend/main.py.pre_PR<NOME>_*" pc_backend/main.py -Force
