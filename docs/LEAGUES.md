# Liga do clube: nomes e vínculo parcial com o save

Investigado em 13/10/2026. A busca usa nomes e códigos somente como chaves internas. O FM aberto não foi usado.

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
