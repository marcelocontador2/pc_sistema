c = open('pc_frontend/index.html', encoding='utf-8-sig').read()

# 1. Corrige a falta de quebra de linha entre } e function
c = c.replace('}function desativarOutrosPeriodos', '}\nfunction desativarOutrosPeriodos')

# 2. Remove o } extra que está sobrando antes do catch
c = c.replace("""    </div>
`;

        }
    } catch (error) {""", """    </div>
`;

    } catch (error) {""")

open('pc_frontend/index.html', 'w', encoding='utf-8').write(c)
print("[OK] Problemas de sintaxe corrigidos no index.html!")
