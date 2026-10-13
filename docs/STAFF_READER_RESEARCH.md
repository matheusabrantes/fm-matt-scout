# Atributos profissionais do staff: investigação do leitor

Verificado em 13/10/2026. Escopo: leitura do arquivo `.fm`, sem abrir o FM, ler memória do processo ou instalar dependências.

## Resultado

Há uma base pública para avançar nos atributos profissionais. O `fmsave` instalado já localiza um bloco de 26 bytes que não publica como atributos; o leitor Rust `gilet` fornece nomes e conversão para esse mesmo bloco. Cargos exatos continuam sem decodificação demonstrada nas fontes examinadas.

O [changelog atual do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/CHANGELOG.md) e a [publicação PyPI](https://pypi.org/project/fmsave/0.5.10/) confirmam 0.5.10 como versão mais recente nesta consulta. A versão não adiciona habilidades profissionais completas. Seu [modelo de staff](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/staff.py) publica apenas adaptabilidade como atributo avaliado; as preferências táticas representam comportamento, não competência.

## Correspondência dos bytes

No [StaffLayout de FM26 26.3.2](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/_layouts/fm26_26_3_2.py), o início é `ability_at = header + 21 + 7 × entry_count`. O [leitor existente](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/readers/staff.py) verifica limites, CA/PA e sentinela antes de aceitar a assinatura.

| Offset relativo a ability_at | Conteúdo |
| --- | --- |
| 0, 2 | CA e PA |
| 13 | Sentinela 12 |
| 14–39 | 26 preferências/valores de escala incompleta |
| 40–65 | 26 valores profissionais e outros, armazenados de 1 a 100 |

O [decoder do gilet](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/staff.rs) identifica os últimos 26 valores como a segunda metade da lista do editor. A conversão é `max(1, (raw + 2) // 5)`. Entre os nomes estão avaliação de capacidade/potencial, gestão de pessoas, motivação, fisioterapia, conhecimento tático, treino ofensivo/defensivo/físico/técnico/tático, posse, goleiros, ciência esportiva e bolas paradas. Dois slots não têm nome; alguns outros são comportamento, não habilidade. Portanto, somar somente uma lista explícita de competências nomeadas, nunca os 26 bytes indiscriminadamente.

Lista conservadora recomendada para **Soma (19 habilidades profissionais)**, com índices relativos ao início `ability_at + 40`: `2` avaliação de capacidade; `3` avaliação de potencial; `4` gestão de pessoas; `5` motivação; `6` fisioterapia; `7` conhecimento tático; `8` treino ofensivo; `9` defensivo; `10` físico; `11` posse; `12` técnico; `13` tático; `15` treino de goleiros/segurar bola; `16` distribuição do goleiro; `18` avaliação de dados; `21` ciência esportiva; `23` negociação; `24` avaliação de staff; `25` bolas paradas. Mostrar a composição da soma.

Excluir `0` Coaching e `1` Coaching Goalkeeping, de significado genérico e possivelmente afinidade de função; `14` Dirtiness Allowance, `17` Versatility e `22` Eccentricity, que não devem aumentar uma nota de competência; `19–20`, sem nome. A adaptabilidade publicada pelo fmsave pode continuar como coluna separada, para não misturar a contagem do bloco. As correspondências com prova específica de editor abrangem 12 dessas 19 competências para Nikolić e 13 para Fradley; as restantes têm a ordem documentada no decoder, com evidência mais fraca.

## Prova local de leitura

Foi feita uma única leitura de uma cópia temporária de COR, build `26.3.2+2329565`, observando os headers que o próprio `fmsave.staff()` aceitou. Nenhum arquivo do jogo foi alterado. Resultado: 10.389 registros de staff, 10.384 headers únicos com habilidade; apenas um registro sem correspondência única, o treinador humano. Registros repetidos de um profissional em clubes não contam como headers diferentes.

| Profissional | CA / PA | Capacidade / potencial | Motivação | Conhecimento tático | Defesa |
| --- | --- | --- | --- | --- | --- |
| Marko Nikolić | 130 / 145 | 12 / 10 | 16 | 13 | 16 |
| Daniel Fradley | 140 / 150 | 12 / 14 | 10 | 16 | 5 |
| Pep Guardiola | 190 / 200 | 18 / 17 | 18 | 18 | 15 |
| Arne Slot | 165 / 175 | 15 / 14 | 14 | 16 | 14 |

Os 12 valores profissionais publicados no [teste do gilet para Nikolić](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/tests/real_save.rs#L1054) e os 13 de Fradley coincidem com esta leitura de COR. Isso confirma a correspondência estrutural e reproduz evidência externa; não substitui conferir a tela do mesmo profissional na mesma data da carreira.

## Limites e integração mínima

A [documentação de formato do gilet, seção 6g](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/docs/SAVE_FORMAT.md#6g-non-player-attributes--solved-on-the-object-one-eid-below) alerta que os primeiros 26 valores mudam para uma escala interna desconhecida em carreiras avançadas. A segunda metade mantém números plausíveis, mas carece de confirmação contra a tela de uma carreira avançada. Tratar esses novos campos como experimentais. Não preencher determinação, disciplina ou trabalho com jovens a partir da primeira metade sem uma decodificação de escala demonstrada.

Reutilizar o header aceito pelo fmsave, conferir CA/PA com o registro público e os limites do objeto antes de ler `+40..+65`. Não associar pelo nome, nem deslocar para o próximo profissional: o UID público do fmsave já representa o header de habilidade que ele vinculou ao profissional. Quando houver ambiguidade, bytes inválidos ou versão incompatível, deixar o campo ausente. A soma deve ficar ausente se faltar qualquer competência incluída.

O [modelo de staff do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/staff.py) rejeita explicitamente `unknown.r4` como cargo: o mesmo código reúne títulos diferentes. O gilet identifica departamentos e o treinador a partir de listas/assentos, mas não resolve a lista completa de cargos atuais. Não inventar nomes como olheiro ou auxiliar a partir de um código ou do maior atributo. IDs continuam sendo chaves internas; a interface pode exibir nomes e valores legíveis.

## Altura, peso e estrutura dos clubes

O [modelo Player do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/players.py) publica `height_cm`, ainda classificado como não confirmado pelo leitor, e não publica peso. O código de jogador/pessoa do gilet também não fornece um decoder de peso em kg. Uma busca por outro leitor encontrou um [importador CSV](https://github.com/vfxper/fm26/blob/main/app/services/README.md), não uma decodificação dos bytes do save; sua coluna weight não comprova que o peso da carreira possa ser extraído.

No [anúncio oficial de desenvolvimento de FM25](https://www.footballmanager.com/news/development-update-football-manager-25-0), a SI anunciou que deixaria de exibir peso nos perfis, preservando uma medida básica interna. Essa declaração é sobre FM25, não uma especificação dos bytes de FM26. Em [entrevista direta sobre FM26 à 3DM, em 09/10/2025](https://en.3dmgame.com/original/912), Miles Jacobson diz que o peso foi substituído por uma medida de tipo corporal. Isso reforça que um código corporal não pode ser tratado automaticamente como quilogramas. Não foi encontrado um decoder confiável de peso em kg nas fontes examinadas; deixar o campo indisponível sem afirmar que ele não existe no save.

Para instalações de treino/formação, academia e status profissional do clube, os leitores examinados também não oferecem novos campos confiáveis. O [modelo de instalações do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/facilities.py) lê apenas instalações corporativas, e declara explicitamente que treino, formação e academia não foram localizados. O [modelo de clube do gilet](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/club.rs) fornece identidade, país e reputação, sem esses ratings ou status. Não reinterpretar o rating corporativo como qualidade de treinamento.

## Integração em 13/10/2026

O adaptador `staff_skills.py` procura headers com UID duplicado, valida o layout do leitor, CA/PA, as 14 preferências nomeadas, sentinel e limites do bloco profissional. Headers ambíguos são descartados. Não altera nem intercepta o leitor instalado. O caminho conservador deixa ausentes os headers alocados com cópias de UID diferentes.

No COR, antes da exclusão de clubes femininos, 10.337 registros receberam as competências. Após a exclusão: **10.333 de 10.385** registros visíveis têm soma completa. Os demais ficam indisponíveis. Nikolić teve soma 207; Fradley, 185; Guardiola, 250. A soma contém somente as 19 competências nomeadas de `SKILLS`, com pesos iguais e máximo 380. Não pretende incluir todos os atributos do FM ou reproduzir ratings proprietários.

Estádios vêm de `save.stadiums()` e de `home_club_uids`, associação pelos jogos em casa; `owner_club_uid` não é usado como estádio do clube. Mais de um estádio associado deixa os valores ausentes. Lugares sentados e capacidade de expansão são medidas separadas, não capacidade total. No Corinthians masculino (UID interno 318), o COR entregou 48.905 lugares sentados e expansão 70.000. Não houve nome de estádio decodificado no levantamento.
