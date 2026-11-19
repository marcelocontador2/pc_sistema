import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
arquivo = Path("pc_backend/main_legado.py")
texto = arquivo.read_text(encoding="utf-8")

errado = 'html_parts.append("</tbody></table>")")'
certo = 'html_parts.append("</tbody></table>")'
count = texto.count(errado)
if count > 0:
    texto = texto.replace(errado, certo)
    print("[OK] Corrigidas", count, "ocorrencia(s) do erro.")
else:
    print("[INFO] Nenhuma ocorrencia do erro exato encontrada.")

import re
padrao = re.compile(r'html_parts\.append\("</tbody></table>"\)"+')
count2 = len(padrao.findall(texto))
if count2 > 0:
    texto = padrao.sub('html_parts.append("</tbody></table>")', texto)
    print("[OK] Corrigidas", count2, "ocorrencia(s) extra(s) do padrao com aspas duplicadas.")

arquivo.write_text(texto, encoding="utf-8")
print("[OK] Arquivo salvo.")
