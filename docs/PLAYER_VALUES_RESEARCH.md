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
