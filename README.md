# FM Matt Scout 26

Aplicativo local de scouting para macOS, inspirado no fluxo do Genie Scout. Versão 0.1 com leitura real de saves FM26 e cobertura parcial da especificação. A leitura usa `fmsave 0.5.10` (MIT); a janela usa AppKit e WebKit. Não há comandos de edição de saves nem acesso à memória do jogo.

## Abrir neste Mac

```sh
open "/Applications/FM Matt Scout.app"
```

Para reconstruir após mudar código:

```sh
./build.command
```

O build usa Python 3.12 instalado em `/opt/homebrew/bin/python3.12`, a `.venv` deste projeto e as ferramentas Swift do macOS. Este aplicativo local depende da `.venv` no caminho atual do projeto. Mover o projeto exige reconstruir. Um instalador independente, assinado para distribuição e notarizado ainda não foi preparado.

A compilação instala e atualiza uma única cópia em Aplicativos, disponível também pela busca do macOS. Feche o app antes de reconstruir. A instalação fica fora do provedor de arquivos da pasta do projeto, que recria metadados incompatíveis com a verificação de assinatura de bundles. O ZIP em `dist/FM Matt Scout.zip` preserva uma cópia sem esses metadados; ele mantém a mesma dependência da `.venv`. Os dados e preferências continuam em `~/Library/Application Support/FM Matt Scout/`.

## Fluxo

Abra uma carreira pelo seletor nativo ou pelos saves encontrados na pasta padrão. Use as abas Jogadores, Staff, Clubes, Minha lista e Meu time. Clique em **Pesquisar / filtros…** para abrir a pesquisa por categorias. As condições são combinadas com AND.

Acima da lista de jogadores, **Sem contrato**, **Expira em até 6 meses** e **Expira em até 12 meses** aplicam a busca com um clique e preservam os demais critérios. Os prazos usam a data da carreira e meses de calendário; contratos já vencidos e datas alternativas sem contrato confirmado ficam fora. Jogadores livres exigem ausência explícita de vínculo e termos atuais; dados incompletos permanecem não identificados. O atalho também fica salvo nos filtros exportados. Os atalhos de lista de transferências e lista de empréstimos usam os estados conferidos no FM para o build 26.3.2; estados não identificados ficam fora. Estar emprestado é diferente de estar listado para empréstimo.

As colunas configuráveis **Rescisão geral**, **Rescisão nacional** e **Rescisão internacional** separam os três tipos; nacional/internacional referem-se ao país do clube atual. Cláusulas por rebaixamento, não promoção e divisão superior ficam fora dessas três colunas. Essas condições aparecem com o nome no perfil. Selecionar um tipo de cláusula no filtro aplica os limites à menor cláusula dos tipos selecionados. Tabela, perfil e filtros de cláusulas, valor de mercado, saldo e orçamento de transferências usam a moeda escolhida em **Moeda / salários…**. Saldos negativos são preservados. A conversão pode ser conferida pelo valor de uma rescisão do perfil aberto, salva por carreira/moeda e independente do período salarial. Sem essa referência, usa a taxa salarial aproximada, quando disponível; sem nenhuma taxa, identifica unidades do save. Filtros salvos conservam os limites na unidade original para manter a mesma busca ao trocar moeda. Detalhes da correção em `docs/CONTRACT_READER.md`.

**Valor de mercado** e **Compra estimada** aparecem por padrão na lista de jogadores, no bloco de mercado e contrato. Layouts antigos são atualizados uma vez, preservando as demais colunas. Depois, suas alterações em Colunas continuam sendo respeitadas. O primeiro prioriza o valor positivo do save e usa regressão nas lacunas; o segundo estima uma taxa de transferência. Ambos têm filtros mínimo/máximo na aba Contrato e ficam salvos nos layouts/filtros. O perfil contratual mostra a origem e os intervalos do modelo. A marca ≈ identifica estimativas. Valores originais, inclusive zero, ficam no perfil e na coluna opcional Valor lido do save. As faixas estimadas não são as faixas exibidas pelo FM nem um preço garantido de proposta aceita. O modelo é experimental: a regressão pura ficou dentro de apenas 1 das 8 faixas observadas em Corinthians/Real Madrid. Fórmulas públicas, versão fixa, adaptações e controles em `docs/PLAYER_VALUES_RESEARCH.md`.

O campo permite selecionar uma ou mais posições com o mouse ou teclado. A busca inclui jogadores com familiaridade de pelo menos 15 em qualquer posição marcada. Clique novamente para remover uma seleção.

Clube, nacionalidade, país onde atua, regiões, tipo de contrato, status no elenco e cláusula têm busca interna e seleção múltipla. Dentro de cada campo as escolhas são OR; entre campos, AND. Por exemplo: Corinthians **ou** Palmeiras, **e** idade até 21, **e** passe mínimo 14. Nacionalidade e sua região consideram todas as cidadanias lidas, incluindo adicionais; o perfil lista cada uma e marca UE. O filtro UE aceita Sim/Não/Qualquer e há coluna correspondente. Movimentos preferidos mantêm AND: o jogador precisa ter todos os traits marcados. Liga do clube agora tem filtro por nome com cobertura parcial das tabelas nacionais do save; detalhes em `docs/LEAGUES.md`.

Ao filtrar por clube, **Todos** inclui a equipe principal e as equipes secundárias vinculadas. O seletor Elenco permite restringir à principal ou às demais. As categorias secundárias usam o número do vínculo no save; os nomes “sub-20”, “reservas”, etc. ainda não foram confirmados pelo leitor. O filtro por clube inclui afiliadas que o leitor vincula ao mesmo clube.

**Soma (36)** = 14 técnicos + 14 mentais + 8 físicos, peso igual. Intervalo 36–720. CA/PA, ocultos, personalidade e goleiro ficam fora dessa soma. Um atributo ausente ou inválido deixa o total indisponível. A soma serve de desempate na ordenação de jogadores. Goleiros têm também uma soma separada de 11 atributos específicos.

Clique em Colunas ou com o botão direito em um cabeçalho para escolher indicadores e atributos individuais. Salvar layout guarda a configuração por lista, disponível ao reabrir o app. Clique normalmente no cabeçalho para ordenar. Abra dois jogadores para comparação pelos marcadores quadrados; os círculos adicionam à lista de observação.

As colunas seguem a mesma ordem na tabela e no seletor. Jogadores: identificação, clube/equipe, capacidade/avaliação, mercado/contrato, características, reputação e atributos por categoria. Staff: identificação, cargo/clube, capacidade, contrato, gestão, treinamento, recrutamento, saúde e personalidade. Clubes: identidade/liga, reputação, elenco, finanças, estádio e cobertura das médias. Layouts existentes são reorganizados preservando as colunas selecionadas. Campos legados do staff ficam em um grupo próprio.

Carregar mais acrescenta linhas abaixo das já carregadas, mantendo os registros anteriores e a rolagem. Linhas por clique permite adicionar 50, 100 ou 200 de cada vez. Alterar filtros, ordenação ou colunas inicia uma nova listagem; mudar apenas a quantidade por clique conserva as linhas atuais. Ao terminar, o botão mostra Todos carregados.

A comparação mostra no topo quantos atributos cada jogador venceu, além de empates e valores ausentes. Jogadores de linha e comparações mistas usam 36 atributos técnicos, mentais e físicos. A seção de goleiro e seus 11 atributos só aparecem e contam se ambos têm familiaridade GK ≥15, totalizando 47. O vencedor aparece em verde e texto; idade, CA/PA e soma não contam como atributos vencidos. Pesos iguais, sem ajuste por tática.

Jogadores, staff e clubes usam o nome curto do clube nas listas, nos seletores e nos cabeçalhos dos perfis, por exemplo Corinthians. A busca aceita também o nome completo, que fica disponível nos detalhes e tooltips. Sem nome curto lido, usa o nome completo como alternativa.

Todas as listas têm uma coluna Nº à esquerda, de acordo com os filtros e a ordenação atuais. Carregar mais continua a sequência; uma nova pesquisa reinicia em 1.

Clubes femininos identificados por IDs de uma referência local são ocultados, incluindo seus jogadores e staff vinculados. Categoria desconhecida permanece visível. No COR foram identificados 1.017, preservando os masculinos homônimos. Sem elenco lido, a contagem mostra Nenhum jogador lido. A referência e sua cobertura parcial estão em `docs/CLUB_GENDERS.md`.

Staff tem colunas Função, Área do staff e Soma de habilidades. O filtro de área permite busca e seleção múltipla nas listas médica, comissão técnica e recrutamento. 23 campos profissionais experimentais estão disponíveis no perfil, nas colunas, nos filtros e na comparação. Soma de 21 competências ativas, peso igual, máximo 420; dois campos antigos de goleiro ficam como legado, fora da soma e do placar; ausente se algum campo não foi lido. Cargos atuais são lidos pelo contrato do mesmo profissional e clube, com filtro pesquisável e seleção múltipla. Assentos identificam treinador principal e diretor de futebol; outros vínculos sem dados suficientes continuam como Cargo não identificado. Preferências e personalidade ficam fora da soma. Fontes/limites em `docs/STAFF_READER_RESEARCH.md`.

Na pesquisa, Salvar filtro guarda os critérios atuais com um nome. Exportar filtros cria um JSON portátil; Importar filtros restaura esses critérios, incluindo clube, posição, elenco, idade, nacionalidade, competição, contrato, atributos e ordenação. Arquivos inválidos são rejeitados sem substituir os filtros existentes. IDs de competições que só existem naquela carreira podem não funcionar em outro save.

## Médias dos clubes

CA médio, PA médio e idade média são ordenáveis. “Equipe principal” usa jogadores no vínculo de equipe 0; “Todos os vinculados” inclui base e reservas. Cada média exclui somente os valores ausentes daquele indicador. Clubes sem jogadores/valores decodificados mostram “—”. O tooltip e o perfil do clube informam a cobertura. As médias de CA/PA e a classificação das equipes mantêm as limitações dos campos de origem.

## Confiança nos dados

O leitor considera `verified` os campos comparados com uma tela do jogo e `unconfirmed` aqueles sem essa confirmação. CA e PA são `unconfirmed` na versão utilizada. O aplicativo os extrai, testa estrutura e intervalos, mas ainda não os conferiu em uma referência independente do mesmo save. O símbolo † conserva essa ressalva.

Notas percentuais são **estimativas Matt Scout**, com pesos e fórmula expostos no perfil. Não reproduzem a fórmula do Genie nem são probabilidades de desempenho. Jev/OpenJev foram discutidos; por decisão do usuário, a integração fica para depois.

Valores monetários usam a moeda selecionada quando existe conversão conferida por carreira/moeda; sem referência, permanecem identificados como unidades do save. Valores totais não recebem o fator de período dos salários. Finanças têm cobertura parcial e uma data própria. Nacionalidades, países e regiões usam nomes em português, com busca e seleção múltipla. Países e movimentos sem nome identificado não são oferecidos como códigos para pesquisa. A liga atual é identificada pelo status do próprio clube, com nomes da instalação local do FM e filtro pesquisável. Tabelas de divisões nacionais servem como alternativa quando esse vínculo não é lido.

Um arquivo opcional `competition-names.csv`, com `database_id,name`, pode fornecer nomes de competições para os dados internos do leitor. O vínculo atual vem do status do clube, separadamente dos nomes.

## Listas, histórico e arquivos

Os dados pessoais do aplicativo ficam em `~/Library/Application Support/FM Matt Scout/`:

- `scout.sqlite3`: listas e snapshots de evolução, separados pelo caminho da carreira.
- `filters.json`: filtros táticos nomeados, formato de exportação versão 1.
- `layouts.json`: colunas de jogadores, staff e clubes.

CSV exporta dados básicos da lista. JSON permite importar a lista de volta no Matt Scout; a correspondência exige ID do FM, nome e nascimento. **CSV e JSON não são shortlists `.fmf` e não são importáveis no FM26.** O formato nativo ainda está pendente.

O histórico registra a primeira leitura de cada data no jogo e jogador naquele caminho. Não reconstrói períodos anteriores. Saves com outro caminho mantêm um histórico separado. Não há envio dos saves à nuvem.

## Verificar

O botão **Salários…** troca moeda (euro, real, libra ou dólar) e período (mensal, semanal ou anual). Euro e mensal são as preferências iniciais. A conversão exige um salário do FM na moeda/período escolhidos, a partir do perfil aberto; fica guardada por carreira e moeda. Até essa conferência, os números são explicitamente unidades do save por semana. Valores abreviados em M ou mil produzem uma conversão aproximada. Filtros de salário e orçamento salarial conservam os mesmos limites ao trocar a exibição, inclusive nos arquivos de filtros. Valor de mercado, cláusulas e saldo não recebem essa conversão salarial.

```sh
.venv/bin/python -m unittest discover -s qa -p 'test_*.py' -v
.venv/bin/python qa/check_save.py "/caminho/da/carreira.fm"
node qa/check_ui.cjs
```

O teste de UI usa o Playwright e o Chromium já disponíveis no ambiente de desenvolvimento deste Mac; seus caminhos estão no script. A comparação dos bytes do save e as verificações da API usam somente a biblioteca padrão do Python. Consulte `docs/COVERAGE.md` para o escopo completo e as pendências.

## Referências

- [Genie Scout 26](https://www.fmscout.com/a-fm-genie-scout-26.html)
- [Guia do Genie](https://www.fmscout.com/a-genie-scout-guide.html)
- [Leitor fmsave e licença MIT](https://github.com/rhiever/fmsave)
- [Critérios de confiança do leitor](https://rhiever.github.io/fmsave/guides/trust.html)

Projeto independente, sem vínculo com Sports Interactive, SEGA ou os autores do Genie Scout.

Altura em centímetros tem coluna ordenável e filtros mínimo/máximo, também salvos nos filtros táticos. Peso em kg ainda sem leitura confiável. Clubes têm colunas de saldo, transferências restantes, orçamento salarial e capacidades de lugares sentados/expansão do estádio pelo vínculo atual do clube, com jogos em casa como alternativa. O nome do estádio pode ser adicionado como coluna e aparece no perfil. Ausência de dados permanece explícita.

Ligas: filtro, coluna e perfil pelo nome nas três listas, pelo vínculo atual do clube e nomes locais do FM. Ausência de vínculo/nome continua explícita como Liga não lida. Detalhes em `docs/LEAGUES.md`. Instalações de treino/formação ainda não têm decoder confiável: `docs/CLUB_FACILITIES_RESEARCH.md`.

Na aba **Clubes**, caixa e orçamentos usam a posição atual quando o registro é reconhecido; o histórico mensal fica como alternativa com origem e data no perfil. A aba **Empréstimos** apresenta valores originais, parcelas, juros mensais e vencimentos dos vínculos lidos, convertidos pela moeda configurada. Esses valores não substituem a dívida líquida atual, cujo cálculo permanece não confirmado.
