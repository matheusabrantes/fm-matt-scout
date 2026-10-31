# Contratos e disponibilidade — conferência de 29/10/2026

Foi lida uma cópia do COR, build `26.3.2+2329565`, data de jogo
30/12/2025, SHA-256
`7010e6db21345f51e2c1a4b00788e21994daae7ae998a271b9d75661f965e8a0`.
O arquivo original não foi editado.

## Jogadores livres

Os 63.514 jogadores possuem um dicionário `contract` na exportação normalizada.
Portanto, `bool(contract)` não indica contrato vigente e tornava a pesquisa
anterior por ausência de contrato vazia.

`contract_reader.contract_state` distingue três resultados:

- `contracted`: o contrato corrente tem clube resolvido e salário numérico
  positivo ou tipo de contrato lido. Um contrato juvenil com salário zero
  continua sendo contrato.
- `free`: a inscrição do jogador está explicitamente ausente (`team_id` e
  `club_uid` são `None`) e o objeto contratual estruturado não contém vínculo,
  salário, tipo, status, eventos ou cláusulas correntes.
- `unknown`: leitura parcial, time não resolvido, ausência do objeto contratual
  ou evidências que não permitem afirmar disponibilidade.

A cadeia pode conservar propostas, transferências futuras e vínculos antigos.
Ela não substitui os campos do contrato corrente. Datas provenientes apenas de
`end_source=player_record` são uma busca alternativa do leitor; não provam
contrato vigente. Por exemplo, jogadores sem inscrição como Paul Ifill e Martín
Silva receberam datas futuras nessa busca. Há também jogadores sem clube
resolvido na inscrição, mas com contrato corrente em outro clube, como Iván Jaime
e José Cifuentes. Eles não podem entrar como livres.

Antes de ocultar clubes femininos, o helper classificou 47.587 registros como
`contracted`, 8.607 como `free` e 7.320 como `unknown`. Entre os desconhecidos,
7.179 têm o contrato totalmente vazio, embora a normalização conserve o
dicionário de chaves preenchidas com `None`. Não foi presumida disponibilidade
nesses casos sem leitura contratual.

## Cláusula de Tiago Gabriel, Lecce

O contrato corrente decodificado para o jogador contém `relegation_release`,
código `1`, valor bruto `864206`; não contém `minimum_fee_release`. A data final
é 30/06/2027. A captura fornecida pelo usuário mostra desmarcadas as cláusulas
geral, estrangeiros e nacionais, mas não mostra a opção por rebaixamento.

O problema demonstrado na apresentação é chamar a menor cláusula condicional de
“Cláusula” sem apresentar a condição. O valor bruto está na unidade monetária
interna do save e não deve receber o símbolo de euro sem conversão conferida.
Na conferência independente do contrato normal do FM, aberta pelo indicador de
salário/expiração no perfil, a seção Cláusulas confirmou **Cláusula de Dispensa
por Despromoção: €1M**, inativa enquanto a condição não ocorrer. A leitura da
condição está correta; eram incorretos o rótulo genérico e o símbolo de euro
aplicado ao valor bruto sem conversão. A coluna geral agora fica vazia nesse caso.

As colunas configuráveis de rescisão geral, nacional e internacional usam,
respectivamente, `minimum_fee_release`, `minimum_fee_release_domestic` e
`minimum_fee_release_foreign`. Nacional/internacional referem-se ao país do
clube atual. Cláusulas com parâmetros adicionais, de divisão superior ou por
rebaixamento não são agregadas nessas colunas. Ausência de leitura aparece como
travessão, sem supor valor zero. Valores base continuam em unidades do save;
a apresentação e os filtros aplicam a conversão por referência descrita abaixo.

## Listas de transferência e empréstimo

O campo `contract.unknown.e39` foi conferido no FM aberto, no mesmo COR de
30/12/2025. A consulta usou Ações → Transferência → Definir Situação de
Transferência e as duas abas; nenhuma seleção foi modificada e todos os
formulários foram cancelados.

- Memphis Depay (13/02/1994, Corinthians, fim 31/07/2028): código 1; na lista
  de transferências e sem estatuto de empréstimo definido.
- Vitinho (09/10/1993, Corinthians, fim 31/12/2026): código 2; disponível
  para empréstimo e sem estatuto de transferência definido.
- Yuri Alberto (18/03/2001, Corinthians, fim 22/07/2030): código 0;
  sem estatuto definido nas duas abas.

`listing_status` exige build 26.3.2, vínculo contratual identificado, fonte
contratual de expiração e contrato vigente na data do save. Somente os códigos
0, 1 e 2 recebem estado. Outros valores (incluindo 3, 64, 65 e 128), contratos
incompletos e outros builds permanecem indisponíveis; não há máscara de bits
inferida nem tratamento de qualquer valor não zero como listado. O filtro
exclui estados desconhecidos e o perfil os diferencia de Não.

Essa cobertura é parcial e experimental. Estar emprestado, ser excedente ou
estar sem clube não foi usado como aproximação de estar listado.

Fontes primárias de apoio: [leitor de contratos do fmsave](https://github.com/rhiever/fmsave/blob/main/src/fmsave/readers/contracts.py)
e [PlayerExporter do FM AI Assistent](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/master/src/main/java/com/github/fmaiassistent/exporter/PlayerExporter.java).
Este último lê memória; seu offset de RAM não foi reutilizado no save.

## Controles adicionais conferidos no FM

No mesmo COR de 30/12/2025, o contrato normal de Lucas Paquetá, Flamengo,
28 anos, nascido em 27/08/1997, até 31/12/2030, mostra **Cláusula de Rescisão
(Clubes Nacionais): €63M**. O leitor retorna `minimum_fee_release_domestic`,
valor bruto `54750000`; não contém cláusula geral nem estrangeira.

O contrato de Vinícius Júnior, Real Madrid, 25 anos, 12/07/2000, até 30/06/2027,
mostra **Cláusula de Rescisão: €1MM** (um bilhão de euros). O leitor retorna
`minimum_fee_release`, valor bruto `864206784`, sem cláusula nacional ou
estrangeira. São controles para distinguir tipos e demonstrar que a moeda
interna não é EUR; as colunas não aplicam uma taxa fixa gravada no código a partir desses exemplos.

## Conversão das cláusulas em 30/10/2026

`SalarySettings` conserva a taxa salarial existente e permite uma referência
monetária separada, `money_rates[carreira][moeda]`, obtida por valor exibido no FM
dividido pelo valor bruto de uma rescisão identificada no perfil. O exemplo
fornecido e conferido de Vinícius é €1.000.000.000 / 864.206.784. Trata-se de
preferência local da carreira, não taxa de mercado ou constante do parser.

Tabela, perfil (incluindo rescisões condicionais) e filtros usam essa taxa sem
multiplicar pelo período salarial. Percentuais e outros parâmetros permanecem
parâmetros. Os limites pesquisados/exportados são unidades originais; trocar
moeda ou período preserva o limite original e aplicar um filtro salvo restaura
a exibição na moeda atual. A validação aceita limites monetários fracionários.

Sem referência própria, uma taxa salarial existente pode ser usada como
aproximação, identificada na interface. Sem nenhuma taxa, permanece bruto com
unidade explícita. Valores de mercado e finanças de clubes não foram incluídos
nesta correção. As taxas não migram automaticamente para outra carreira/moeda.

O FM abrevia e arredonda valores: com a referência do Vinícius, o valor bruto
864.206 de Tiago resulta em aproximadamente €999.999,09, a menos de €2 do €1M
abreviado pelo FM. A leitura serializada inteira e a exibição abreviada não
permitem certificar centavos para todas as cláusulas.
