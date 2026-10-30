# Staff: atributos profissionais e cargos

Atualização dos atributos em 30/10/2026: o adaptador passou de 19 para **23
campos profissionais decodificados**, incluindo autoridade, trabalho com jovens,
determinação e treino de goleiros. A soma atual usa 21 competências e tem
máximo 420; os dois campos antigos de goleiro ficam como legado, fora da soma.
As escalas,
contagens e a conferência numérica de Célio Silva no FM estão em
[`STAFF_ATTRIBUTES_RESEARCH.md`](STAFF_ATTRIBUTES_RESEARCH.md). As seções
abaixo preservam o histórico e as medições das versões anteriores.

Verificado em 13/10/2026. Escopo: leitura do arquivo `.fm`, sem abrir o FM, ler memória do processo ou instalar dependências.

## Resultado

Há uma base pública para avançar nos atributos profissionais. O `fmsave` instalado já localiza um bloco de 26 bytes que não publica como atributos; o leitor Rust `gilet` fornece nomes e conversão para esse mesmo bloco. Na consulta inicial, as fontes examinadas não demonstravam a decodificação de todos os cargos. O avanço no contrato atual está na seção de 29/10/2026 ao final deste documento.

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

## Cargos atuais: avanço em 29/10/2026

O contrato do staff tem um byte de cargo imediatamente depois do salário semanal de quatro bytes, em `tag + 21` no layout `26.3.2+2329565`. É um campo diferente de `r4` no bloco de habilidade. A leitura de COR, salvo em 30/12/2025, mostra por que essa diferença importa: Célio Silva tem `r4 = 80`, mas o contrato contém `14`; William Batista tem `r4 = 2`, mas o contrato contém `16`; Bruno Gorgatte tem `r4 = 0`, mas o contrato contém `50`.

A nomenclatura dos códigos comuns foi comparada com o [`jobName` do leitor aberto FM AI Assistent](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/master/src/main/java/com/github/fmaiassistent/exporter/StaffExporter.java). Esse projeto lê memória; seu [offset de cargo em RAM](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/master/src/main/java/com/github/fmaiassistent/memory/StaffRecordLayout.java) **não** foi usado como offset do save. A posição no arquivo foi identificada e verificada separadamente. O perfil aberto de Nicolas Jover no FM, 44 anos, nascido em 02/04/1981 e no Arsenal, confirmou `22` como Preparador de Lances de Bola Parada; o mapa de RAM chama esse código incorretamente de Performance Analyst. Por isso, códigos sem rótulo demonstrado continuam ausentes e o mapa inclui apenas códigos encontrados nesta leitura.

O código `62` foi conferido em dois perfis abertos: Raony, 36 anos, 19/03/1989, Corinthians, contrato até 31/12/2027; e Toni Tapalović, 45 anos, 10/10/1980, Barcelona, contrato até 30/06/2027. Nos dois, o cargo exibido abaixo do clube é literalmente **Coordenador de Análise de Recrutamento**. A categoria profissional abaixo do nome e o histórico apresentam títulos diferentes; para Raony a categoria é Analista de Desempenho, enquanto Toni tem Treinador Adjunto Principal e histórico de treino de goleiros. O app segue o cargo do vínculo atual exibido pelo FM, sem reinterpretá-lo pela categoria, pela biografia, pelo departamento ou pela profissão fora do jogo. Não foi determinado se essa divergência é uma particularidade de tradução ou dos dados da carreira.

O adaptador `read_staff_contract_roles` usa o localizador de contratos do `fmsave`, exige o header da própria pessoa, decodifica o contrato completo e confere UID, clube, equipe, salário e datas com o registro de staff já lido. Contratos futuros ou expirados são rejeitados. Mais de um contrato correspondente deixa o cargo ausente. Um código desconhecido ou contrato sem termos também não recebe um nome. A integração deve manter a verificação do build já usada para os assentos; não estender este offset a outro layout sem nova prova.

A checagem independente pelos assentos produziu estes resultados no COR atual:

- Dos 2.122 assentos de treinador, 2.110 têm código `16` no contrato. Os outros 12 têm funções acumuladas de diretor, proprietário ou presidente.
- Dos 213 assentos de diretor de futebol, 211 têm código `10` e dois têm código `6` (diretor).
- Os departamentos separam os códigos de forma consistente: fisioterapeutas, cientistas e chefias médicas aparecem na lista médica; olheiros, chefias e diretor técnico, na lista de recrutamento; preparadores, auxiliares e treinadores, na lista técnica.

Por isso, os assentos próprios continuam tendo prioridade quando uma pessoa acumula funções. O código `16` do contrato significa Treinador, sem afirmar que é o principal: William Batista foi conferido no FM e trabalha na base. O novo decoder de contratos identificou **9.850 de 10.541 registros** de staff antes da exclusão de clubes femininos, em **25 cargos distintos**, já rejeitando contratos futuros/expirados. Assentos e treinador humano são integrados separadamente. Essa contagem não é uma validação visual de cada profissional. Os códigos `58` (Renan Bloise, Analista de Recrutamento) e `60` (Guilherme Lyra, Analista de Desempenho) foram conferidos na busca do FM e ainda aguardam a confirmação do perfil aberto; outros registros não têm contrato completo ou associação única demonstrada. Não usar `r4`, o maior atributo ou uma preferência para preencher os restantes.

A leitura foi feita de cópia temporária, conferindo tamanho e mtime do save original antes e depois. Os testes do adaptador cobrem a divergência entre `r4` e o contrato, correspondências de clube/equipe/UID/salário/datas, duplicidade, contrato incompleto e código desconhecido.

Na extração dos pendentes em 30/10/2026 (mesmo COR de 30/12/2025), os 688
registros sem cargo se repartem em 627 sem contrato lido, 57 sem associação ao
header de habilidades e quatro contratos futuros. Os seis do Corinthians são
Eures Soncini Facci, Giulio Cesare Lopes Ferriello, João Marcelo, Leandro Correia
dos Santos, Michel Youssef Muniz Domingos e Ricardo Galotti. Os nomes completos
de Eures e Ricardo não retornaram resultado na busca global do FM; isso não
prova ausência de vínculo nem permite nomear a função. O perfil aberto de
Adryan Almeida, Guarani, 46 anos, 09/06/1979, confirmou o cargo atual Analista de
Desempenho abaixo do clube. Ele integra o grupo sem header associado; a categoria
profissional abaixo do nome diz Analista de Recrutamento, reforçando que a
categoria não substitui o cargo do contrato. Nenhum nome foi usado como exceção
fixa no mapa de cargos. A lista completa ficou em CSV local, fora do Git.

## Vínculos restantes: correção em 30/10/2026

A nova leitura do COR usa o arquivo salvo em 30/12/2025, SHA-256
`3795481a7bebcdd4512f3c1419b3c0890adda042dc1f5fa74cb73b92874cde8d`.
A cópia e os dados descomprimidos foram compartilhados com a investigação de
finanças; não foi criada outra cópia nem alterado o save.

O primeiro bloqueio era o pré-filtro deste aplicativo: ele exigia duas cópias
iguais do UID, embora `_header_values(..., layout)` do `fmsave==0.5.10` já aceite
headers alocados com palavras diferentes, quando tipo e bloco completo são
válidos. O candidato agora também alcança esse caminho. A atribuição continua
exigindo UID, tipo, CA/PA, preferências nomeadas e bloco profissional íntegro;
mais de um bloco correspondente continua ambíguo. Adryan Almeida tem selector
75679 nesse save e passa por esse caminho, com cargo contratual Analista de
Desempenho. Não foi usado o nome como chave de correção.

O segundo bloqueio era uma forma distinta de registro médico que o decoder de
contratos completos não publica como contrato. Os 629 registros sem contrato
lido possuem uma atribuição médica desse tipo. O adaptador aceita somente a
forma demonstrada do build 26.3.2, com os seguintes offsets relativos:

| Offset | Dado usado |
| --- | --- |
| +8 | Marcador de forma `06 00` ou `0a 00` |
| +10 | Referência de quatro bytes, opaca (pode ser ausente) |
| +14 | Marcador `05 05` |
| +16 | Selector da própria pessoa |
| +20 | Equipe que resolve no índice do save para o clube que a lista |
| +28 | Campo monetário opaco; não publicado como salário por este adaptador |
| +32 | Cargo: 38 ou 46 |
| +34, +35..38 | Zero e sentinela `FF FF FF FF` |

O registro precisa estar na janela do header da própria pessoa. Sua distância
ao fim do bloco de habilidades validado é uma das três formas observadas:
77, 80 ou 88 bytes. Exige listagem médica atual no clube e ausência de contrato
completo já lido. Mais de um registro aceito, equipe sem clube correspondente,
identidade diferente, prefixo incompleto ou cargo fora dos dois códigos deixa
esse adaptador sem resultado. Os campos de data dessa forma ainda não foram
identificados; não foram chamados de início/fim nem usados para criar termos.
A equipe usa o clube armazenador, preservando médicos de equipes B que não têm
um contrato completo que os transfira para o controlador da afiliada.

O byte de cargo dessa forma é independente de `unknown.r4`: Fernando Modesto de
Sousa (Esporte Clube Flamengo) tem `r4=6` e atribuição médica 46; Reinaldo Couri
Nogueira (Volta Redonda) tem `r4=46` e atribuição 38; Leandro Correia dos Santos
(Corinthians) tem `r4=0` e atribuição 38. Essa diferença impede preencher os cargos
pelo byte de preferência ou pelo departamento sozinho.

A conferência no FM da página pública de todos os funcionários do Real Madrid
mostrou Felipe Segura, 51 anos, e Manuel Arroyo, 50, como **Médico**, com nomes
sem link para perfil, salário N/D e expiração N/A. Niko Mihić, 69, aparece como
**Director Clínico**. Isso confirma 46 como Médico e 38 como Diretor clínico.
O identificador interno `club_doctor` foi preservado para 38 para não invalidar
filtros existentes; seu rótulo visível foi corrigido.

Na cópia examinada, a nova forma cobre 629 atribuições: 315 diretores clínicos
e 314 médicos, sem inferir por nome. Os seis pendentes do Corinthians passam a
ter cargo: Leandro é Diretor clínico; Giulio Cesare Lopes Ferriello, Eures Soncini
Facci, Ricardo Galotti, Michel Youssef Muniz Domingos e João Marcelo são Médicos.
O app registra `has_club_appointment` e a origem `club_appointment` para distinguir
a confirmação de emprego da leitura de termos contratuais. Não inventa salário,
vencimento ou período; o campo original `has_contract` do leitor é preservado.
O estado normalizado de vínculo passa a contratado, de acordo com o contrato
Profissional exibido pelo FM, sem marcar como lidos os termos ausentes.

A prova combinada no arquivo novo resultou em **10.537 cargos identificados de
10.541 registros brutos**, antes da exclusão de clubes femininos. Restam quatro
vínculos com início posterior à data da carreira: Michael Wiesinger (Bayern,
01/05/2026), Tobias Weis (Sportfreunde Schwäbisch Hall, 01/07/2026), Benjamin
Le Reste (AS Miquelonnaise, 01/05/2026) e Marc Heidenmann (RB Leipzig,
01/07/2026). Não foram apresentados como cargos atuais antes do início.

Os headers alocados acrescentaram 53 pessoas distintas, distribuídas em 57
registros de clube. **10.540 registros brutos** receberam as 19 habilidades,
ficando ausente somente o treinador humano. Treze testes específicos de staff
passaram, incluindo o percurso completo de atribuição médica sem inventar termos,
UIDs alocados, ambiguidade, dono/clube/equipe, limites e sentinelas. A prova local
foi guardada com o hash da fonte em `staff-reader-verification.json`, no diretório
temporário compartilhado, sem publicar o save nem recortes binários no Git.
