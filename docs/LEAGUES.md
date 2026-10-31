# Liga atual e estádio do clube

## Leitura direta em 30/10/2026

`club_locations.py` lê a divisão **atual** e a referência do estádio no objeto de status do próprio clube. O parser aceita somente `26.3.2+2329565`, exige o índice do clube conferido contra seu registro básico, as duas cópias do identificador, dez bytes de confirmação zerados, tipo normal `0x0A` e reputação válida. Objetos duplicados ou sem dono inequívoco ficam ausentes.

Os offsets abaixo partem da primeira cópia do identificador no objeto de status:

| Offset | Campo | Espaço de identificação |
| --- | --- | --- |
| +13 | Divisão atual, u32 | Entidades de competição do save |
| +17 | Divisão anterior, u32 | Não utilizada para a liga atual |
| +25 | Estádio principal, u32 | Ordinal do estádio do fmsave + 1 |

A associação de competição usa os pares estruturais já validados pelo `fmsave.readers.competitions.locate_competition_database_ids`. O campo direto estabelece que essa entidade é a divisão do clube; não exige que ela tenha calendário ou uma tabela de classificação simulada. A lista de `save.competitions()` sozinha excluiria 14.526 clubes com divisão nomeada porque eles não têm estágios carregados no COR. Não se deduz a liga pelo país, reputação, participantes de uma copa ou base inicial.

Os nomes são lidos localmente do `lang_db.dat` **instalado com o FM**, na pasta padrão do Steam para Mac. São descomprimidos apenas o diretório e os dois frames necessários, com limites de tamanho. As tabelas PT-BR `19_25` e `19_21` têm, respectivamente, 7.947 competições e 50.907 estádios, ambas verificadas até o último byte. Nenhuma cópia integral dessas tabelas proprietárias é distribuída com o aplicativo. Se o FM não estiver nessa pasta, se a base não tiver o formato reconhecido ou se um nome faltar, o nome permanece desconhecido; o pequeno mapa `league-names.csv` continua disponível como referência anterior.

### Identidade dos estádios

O identificador público de estádio produzido pelo fmsave é o identificador do cabeçalho + 1. Ele não é, em geral, a chave da tabela instalada de nomes. O corpo de um registro é nomeado pelo identificador armazenado no **cabeçalho seguinte**, cujo ordinal deve ser consecutivo. A diferença fica visível quando há lacunas nos IDs: o estádio principal do Corinthians tem UID público 19.141.016, mas o cabeçalho seguinte armazena 19.141.329, que identifica **Neo Química Arena** na localização. Somar um ao primeiro ID produziria um nome ausente ou errado. O Santiago Bernabéu não evidencia esse problema porque seus IDs são consecutivos.

O exame independente do frame 22 de `server_db.dat` instalado confirmou a mesma sequência: corpo com 48.905 assentos, cabeçalho armazenado 19.141.015 e próximo cabeçalho 19.141.329. No save, o vínculo de status do Corinthians aponta diretamente para esse corpo. A capacidade é lida do save, e o nome é rotulado como referência da base instalada. Um nome inline do próprio save tem prioridade. O último registro, sem cabeçalho seguinte de estádio, não recebe nome externo por aproximação. Um nome da base instalada pode não refletir uma alteração de nome sem string inline legível no save.

### Probe COR

Antes da exclusão de clubes femininos, foram encontrados 33.593 status de clubes com identidade confirmada, 26.574 divisões nomeadas, 28.934 vínculos diretos a estádio e 28.842 estádios principais nomeados. Esses números são do snapshot COR de 30/10; não são uma garantia de cobertura para toda carreira.

| Clube | Divisão atual | Estádio | Assentos no save |
| --- | --- | --- | ---: |
| Corinthians | Brasileirão | Neo Química Arena | 48.905 |
| Liverpool | Premier League | Anfield | 61.276 |
| Manchester City | Premier League | City of Manchester Stadium | 53.400 |
| Bayern | Bundesliga | Allianz-Arena | 75.000 |
| Real Madrid | Primeira Divisão Espanhola | Santiago Bernabéu | 83.186 |

`qa/test_club_locations.py` verifica divisão atual diferente da anterior, rejeição de dono/incorporação/versão inválidos, duplicatas, truncamento, referências ausentes, lacunas nos IDs dos estádios, prioridade do nome inline e formatos dos nomes. A conferência visual no FM é registrada separadamente pela tarefa principal.

## Histórico: vínculo parcial por tabelas

O restante desta seção registra a implementação anterior, substituída pela leitura direta acima quando disponível. Investigado em 13/10/2026. A busca usa nomes e códigos somente como chaves internas. O FM aberto não foi usado.

## Origem dos nomes

`league-names.csv` contém 56 divisões nacionais seniores, selecionadas explicitamente; não é uma lista de todas as competições. Os nomes foram lidos do arquivo instalado do próprio FM26, `shared/data/database/db/2600/2600_fm/lang_db.dat`, seção `19_25.dat` da língua portuguesa brasileira. O arquivo tem um prefixo TAD de 12 bytes seguido de contêiner FMF/Zstandard; o índice e a descompressão foram lidos com o [contêiner do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/_container.py). Nenhum arquivo instalado foi alterado.

A seção de competições tem assinatura TAD, contagem u32 e registros `database_id:u32`, seguidos de três strings UTF-8 com tamanho u32 e terminadores: nome longo, curto e sigla. Foram lidos exatamente 7.947 registros até o último byte, sem sobras. Somente os 56 nomes selecionados foram incorporados ao produto, conferidos byte a byte com a seção. SHA-256 do `lang_db.dat`: `423386492ea49c06ce7a4faef291666089fe66a70fcf916d5616977f2777fe76`.

Os nomes são uma referência da base instalada, não uma suposição a partir dos clubes de uma tabela. Não fornecem por si só a liga atual. Bases personalizadas ou alterações de nomes podem exigir atualizar essa referência. Copas continentais, ligas de seleções e competições de formação não estão na lista.

## Vínculo da carreira

A [tabela do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/league_tables.py) fornece o `club_uid`, o slot de equipe e a competição que o calendário consegue vincular. A [competição](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/competitions.py) fornece seu `database_id`. O aplicativo só aceita competições na lista explícita de divisões nacionais e registros de equipe principal (`team_slot == 0`). Não classifica uma tabela pela quantidade de clubes ou por suas equipes: a Champions feminina também tem uma tabela de 18 clubes neste save.

Se houver um único identificador de liga por clube, o nome é propagado aos jogadores e staff pelo vínculo do próprio clube. Repetições da mesma tabela são consolidadas. Se houver duas ligas nacionais candidatas, o clube permanece sem ligação: não se escolhe uma arbitrariamente. Clubes sem tabela nomeada mostram **Liga não lida** e não correspondem a filtros de liga; isso não significa que não tenham divisão no jogo. O vínculo é experimental, herdando os limites de associação tabela/calendário do leitor.

## Resultado COR

Foram vinculados **150 clubes**, em oito competições:

| Liga | Clubes |
| --- | ---: |
| Premier League | 20 |
| Ligue 1 McDonald's | 18 |
| Bundesliga | 18 |
| VriendenLoterij Eredivisie | 18 |
| Serie A | 20 |
| Torneo Apertura 1ª Divisão Mexicana | 18 |
| Primeira Liga Portuguesa | 18 |
| Primeira Divisão Espanhola | 20 |

Corinthians masculino não aparece em uma tabela nacional utilizável nessa leitura. Seu nome de liga permanece ausente, embora Brasileirão esteja no mapa. Nenhuma liga foi atribuída pela reputação, nacionalidade, base inicial de clube ou jogos de copa.

## Limites

Ainda não foi decodificado o campo direto de divisão atual de todos os clubes. A ligação agora é útil nos clubes cobertos pelas tabelas, mas não cobre os 32.867 clubes visíveis do COR, equipes fora das ligas simuladas ou temporadas ainda sem tabela utilizável. Promoção/rebaixamento e estruturas especiais não são reconstruídos. A interface informa a cobertura, permite selecionar várias ligas pelo nome e preserva filtros/colunas.

## Conferência visual no FM em 30/10/2026

Na carreira COR, data 30/12/2025, as páginas dos próprios clubes confirmaram Corinthians / Brasileirão - Série A / Neo Química Arena; Bayern / Bundesliga / Allianz-Arena; Real Madrid / La Liga Santander / Santiago Bernabéu. O vínculo da divisão é o mesmo, mas nomes comerciais/customizados do jogo podem diferir da base localizada instalada (por exemplo, Primeira Divisão Espanhola). Não houve alteração de valores no editor.

Após ocultar os 1.017 clubes femininos de referência: 32.867 clubes visíveis, 25.593 com divisão atual nomeada e 27.933 com estádio nomeado no probe direto. Esses números não incluem eventuais vínculos alternativos por calendário/tabelas.
