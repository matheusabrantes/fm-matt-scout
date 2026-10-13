# Exibição de salários

Padrão: euro por mês. Opções: EUR, BRL, GBP e USD; mês, semana e ano. Preferências locais em `~/Library/Application Support/FM Matt Scout/salaries.json`. Cada moeda tem uma conversão por carreira (caminho do save).

O [leitor fmsave](https://rhiever.github.io/fmsave/reference/records.html) informa salário semanal na unidade interna do save. Não fornece a moeda dessa unidade; não foi assumido que ela seja libra ou euro, e não se usa câmbio externo do dia.

Abra o perfil de um profissional e Salários. Informe o salário exibido no FM, na moeda e período selecionados. A taxa é `valor informado / (salário semanal lido × fator de período)`, com fatores 1, 52/12 e 52. Sem referência válida, a preferência pode ser salva, mas valores continuam explicitamente em unidades semanais do save. Uma moeda sem taxa própria não reutiliza a taxa de outra moeda ou carreira.

Referência informada pelo usuário para COR: Vinícius Júnior, **€ 1,72M**, interpretado como mensal conforme o padrão pedido. O leitor retornou 344.735 unidades semanais; fator para EUR 1,1513860702367817. Isso reproduz € 1.720.000/mês para esse jogador. Como o valor informado está abreviado, essa conversão é aproximada; não foi confirmada com um valor mais preciso da tela do jogo. Um valor exato pode substituir a referência no diálogo.

A tela do FM aberto foi lida depois e confirmou “€ 1,72M p/m”, eliminando a dúvida sobre o período. O valor continua abreviado, e não houve extrapolação de confirmação para todos os contratos.

Tabela, perfil de contrato, limites de salário e orçamento salarial usam a preferência. Ordenação permanece na unidade original, preservando a ordem porque o fator é positivo. Filtros salvos armazenam os limites na unidade original e voltam para a apresentação escolhida ao restaurar. Outros valores monetários não recebem automaticamente esta conversão salarial.

Os testes de UI conferem a mecânica usando um fator sintético de 1,2 em storage temporário. Esse fator não é aplicado aos dados persistentes do usuário.
