# DESATIVADO INTENCIONALMENTE.
#
# A dashboard (index.html) agora e 100% client-side: o proprio JavaScript
# busca os CSVs da planilha Google ao vivo no navegador (fetch + _parseGAds/_parseMeta).
# Portanto este gerador nao e mais necessario.
#
# A versao anterior deste script tinha bugs graves:
#   - descartava campanhas que nao fossem Branding/Demanda/Segmentos
#     (ex: "Contratos B2B" ficava invisivel, subcontando o investimento);
#   - injetava os dados no lugar errado do HTML, DUPLICANDO/CORROMPENDO o
#     arquivo a cada rodada (o que quebrava os filtros de data).
#
# Por isso foi neutralizado: nao le nem escreve mais o index.html.
# Como nao ha alteracao no arquivo, o workflow nao gera commit e nada e corrompido.
#
# (Para reativar uma geracao estatica no futuro, reescrever este script para
#  ler TODAS as campanhas e gravar o HTML de forma integra.)

print("update_from_sheets.py desativado — dashboard e client-side. Nada a fazer.")
