# Valores de jogadores e faixas do FM26

## Fonte atual e lacunas

O aplicativo usa `Player.transfer_value`, do `fmsave==0.5.10`, em unidades
monetárias internas do save. A conversão para a moeda escolhida é uma etapa
separada. A faixa exibida pelo FM e o preço pedido pelo clube não são o mesmo
campo deste leitor.

No layout `26.3.2+2329565`, o campo está em `record_offset + 93`, depois dos
atributos e antes da data de entrada no clube. O leitor distingue quatro estados:

| Estado | Conteúdo | Tratamento atual |
|---|---|---|
| `ok` | Número positivo diferente do sentinela | Valor disponível |
| `zero` | `0` | Publica zero; não implica ausência de contrato |
| `unset` | `0xFFFFFFFF` | Não definido |
| `placeholder` | `300000000` | Sentinela, não € 300 milhões |

Uma verificação somente de leitura do `game_db.bin` da carreira COR, data
30/12/2025, encontrou 63.189 registros aceitos pela passagem de marcadores:
39.908 `ok`, 15.079 `zero`, 6.934 `unset` e 1.268 `placeholder`. Essa contagem
não inclui a passagem complementar do leitor, portanto não equivale ao total
de jogadores mostrado no aplicativo.

Entre os 68 jogadores vinculados ao Corinthians na API antes da correção, 16 não tinham
valor. Vítor Manoel, Guilherme Pires, Molina, Favela, João Disaró e Léo Agostinho
foram conferidos diretamente no registro: todos armazenam zero nesse campo,
apesar de possuírem vínculos contratuais. Harry Kane, do Bayern, armazena o
sentinela `300000000`. Não é um erro de conversão de euros nem evidência de que
esses jogadores possam ser contratados de graça.

No FM aberto na mesma data, Vítor Manoel, do Corinthians Res., mostrou
**valor € 0**, salário € 360/mês e contrato até 28/02/2026. Esse controle
confirma que descartar todo zero apagava informação válida. O adaptador
`player_values.py` agora preserva esse zero, sem alterar `contract_state`,
e expõe `value_source`, `value_status` e uma explicação para o perfil.
Sentinelas e campos ausentes continuam sem número.

## Pesquisa de implementações e fórmulas

- A [referência atual do fmsave](https://rhiever.github.io/fmsave/reference/records.html)
  continua expondo valor e estado, sem limites de uma faixa de mercado.
- O [FMSuperScout](https://github.com/mavarobli/FMSuperScout) lê um valor de
  memória para parte dos jogadores e estima os demais. Seu
  [decoder](https://github.com/mavarobli/FMSuperScout/blob/main/plugin/Dumper.cs)
  usa os mesmos sentinelas `0xFFFFFFFF` e `300000000`; os offsets de RAM do
  Windows não são offsets do save nem do processo do FM no Mac.
- A [documentação do modelo](https://github.com/mavarobli/FMSuperScout/blob/main/docs/value-model.md)
  descreve uma regressão própria baseada principalmente em reputação, idade
  e duração de contrato. Não apresenta uma fórmula oficial do FM. Também
  registra problemas com adolescentes e jogadores fortes de reputação baixa.
  Uma faixa desse modelo precisa ser identificada como estimativa do modelo,
  sem substituir o valor lido ou se apresentar como a faixa mostrada no jogo.
- O [guia do Genie Scout](https://www.fmscout.com/a-genie-scout-guide.html?dcm=2&e=page)
  distingue valor e *Sale Value*. A página atual de
  [funcionalidades](https://geniescout.com/features/) chama o último de estimado.
  Isso não fornece um algoritmo público verificável para reproduzi-lo.

## Limite da investigação

O registro principal e os estados acima foram conferidos; ainda não foi
demonstrado um decoder dos dois extremos da faixa, de um valor alternativo
ou de uma fórmula equivalente à do FM. Encontrar números próximos de um
registro não prova sua finalidade. Os termos contratuais, cláusulas e preço
pedido não podem preencher esse campo por semelhança numérica.

O próximo controle útil é confrontar um jogador `placeholder` com a faixa e,
se disponível, o valor interno mostrado pelo editor do jogo, na mesma data da
carreira, preservando o save. Ausência de leitura permanece diferente de
valor de mercado zero.

## Controles adicionais no FM

Harry Kane, Bayern, na mesma data, mostrou **Não está à venda**, sem faixa numérica no cabeçalho. Seu marcador de 300 milhões não foi tratado como valor monetário nem como preço pedido. Esse controle isolado não demonstra que todo marcador tenha o mesmo motivo.

O [manual oficial de transferências do FM24](https://community.sports-interactive.com/sigames-manual/football-manager-2024/transfers-recruitment-and-scouting-r4962/) distingue valor e provável exigência do clube, e descreve propostas parceladas e negociação; não fornece uma fórmula universal. A versão do manual é anterior ao FM26. O [experimento do autor do fmsave no Reddit](https://www.reddit.com/r/footballmanagergames/comments/1wndzpf/i_parsed_101k_players_in_a_fresh_fm26_save_to/) ajusta valor em função de idade/CA/PA para encontrar jogadores subvalorizados; não valida o preço aceito numa negociação nem os extremos da faixa.

## Modelo adotado — 30/10/2026

A pedido do usuário, `value_model.py` implementa independentemente as equações
publicadas no [código FMSuperScout fixado em cd0062e](https://github.com/mavarobli/FMSuperScout/blob/cd0062e0e51ca57bbed5ef0268a04427e3655afd/app/app.js#L1027-L1140).
A documentação da origem estava divergente do código atual, principalmente
no multiplicador de listados. Os números abaixo seguem o código dessa versão;
não foi incorporado o JavaScript do projeto nem adicionada dependência.

Para lacunas: `ln(V) = 10,96 + 0,997 × reputação_saturada/1000 − 0,069 × idade
− 0,041 × potencial_jovem + 0,507 × ln(máximo(2, meses))`.
Reputação saturada mantém até 7.500 e adiciona 30% do excedente. Potencial jovem
é PA−CA não negativo até 21 anos, metade entre 22–24, zero depois.
Sem prazo lido, usa 36 meses; até quatro meses, aplica ×0,7. Arredonda para
100 mil a partir de um milhão e 10 mil abaixo. Faixa: ±50% até 20 anos,
±35% depois. Reputação mundial zero usa 3.000, com a hipótese exposta no perfil.

Valor positivo do save tem prioridade e faixa própria de ±15%. Zero original
continua zero no campo original; uma estimativa adicional não altera seu estado
contratual. Sentinelas nunca viram valor real. Dados incompletos de idade,
CA/PA, reputação ou vínculo, contratos vencidos/futuros e datas inválidas
não geram estimativa. Sem contrato confirmado: taxa zero, sem incluir luvas,
salário ou comissões. As faixas são heurísticas, sem confiança estatística medida.

Compra usa o valor acima. Listado para transferência tem multiplicador 1;
os demais usam `clamp(0,7 + 0,014 × meses, 0,6, 1,35)`, com 30 meses se ausente.
Ajusta idade/potencial, posição salarial no clube (mínimo oito salários lidos,
empates preservados, agrupamento por UID do clube) e diferença de reputação
comprador/vendedor quando há um único clube gerenciado identificado. Limite
final ×0,4–1,7, faixa ±15%. Não aplica “não está à venda” nem “será dispensado”
porque esses estados ainda não têm decoder confirmado; não infere a partir de
sentinelas, ausência de clube ou salário. A fonte também não cobre concorrência,
orçamento e comissões. Não usamos salário/período como preço de compra.

A saída matemática usa a escala monetária interna do valor de origem. Tabela,
perfil e filtros aplicam a conversão monetária já conferida para a carreira;
o período salarial não afeta essas estimativas. Sem taxa, mostram unidades do
save. As aproximações do modelo não se tornam exatas após conversão.

### Conferência contra as faixas do FM

COR, 30/12/2025, jogo aberto, somente leitura. **Ambos os clubes exibem faixas**,
inclusive o Corinthians gerenciado. Controles em `qa/fixtures/value-model-controls.json`.
Euros convertidos pela cláusula geral de Vinícius: `1e9 / 864206784`.

| Jogador | Faixa exibida pelo FM (€ M) | Valor do save (€ M) | Regressão pura (€ M) |
|---|---:|---:|---:|
| Hugo Souza | 9,4–11,5 | 10,12 | 6,13 |
| Yuri Alberto | 10–13 | 12,98 | 4,86 |
| Breno Bidon | 12–14 | 12,15 | 0,75 |
| Rodrigo Garro | 10,5–13 | 11,25 | 2,66 |
| André Ramalho | 0,6–0,95 | 0,94 | 1,27 |
| Vinícius Júnior | 111–169 | 152,21 | 131,80 |
| Kylian Mbappé | 298–357 | 303,68 | 238,14 |
| Jude Bellingham | 193–215 | 193,50 | 184,68 |

O valor do save caiu dentro de 8/8 faixas; a regressão pura, 1/8. Isso sustenta
priorizar o campo lido, **não valida a regressão nas lacunas**. O caso Breno
mostra uma subestimação grande. Não houve ajuste de coeficientes para forçar
esses oito controles, nem uso do meio da faixa como valor real. Não foi
negociada nenhuma transferência, então os controles não validam o preço aceito.
As faixas reais foram observadas para conferência e não são preenchidas no app
por uma tabela de nomes fixos. O decoder dos extremos da faixa continua pendente.
