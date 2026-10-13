# Categoria dos clubes

O leitor fmsave 0.5.10 não fornece gênero do clube. `club-genders.json` guarda uma referência local de IDs de clubes do FM26 e sua categoria, consultada em 12/10/2026 na [base de clubes do Footyshoe](https://footyshoe.com/players/fm26/clubs?gender=Female). São 1.499 IDs femininos, obtidos das 38 páginas do filtro Female; a página 39 estava vazia. Os 40 IDs masculinos são da primeira página do filtro Male. A data de banco declarada nos perfis dessa fonte é 07/07/2025.

O aplicativo usa somente ID e categoria dessa referência, sem importar jogadores, médias, finanças ou ratings do site. Não há consulta de rede durante a leitura do save.

O fmsave expõe o identificador de fechamento com incremento de 1: a comparação usa `Club.unique_id - 1`, não o `uid` transitório, nem o nome. Essa normalização foi conferida para Chelsea, Arsenal, Manchester City, Barcelona e Bayern. Exemplo: a referência identifica [Chelsea 2000099871 como feminino](https://footyshoe.com/players/fm26/clubs/2000099871/chelsea); o registro correspondente no save COR tem `unique_id=2000099872`. Atualizar a versão do leitor exige reconferir essa regra.

No COR, 1.017 clubes corresponderam à referência feminina e foram ocultados. As versões masculinas dos cinco clubes homônimos citados permaneceram. Jogadores e staff vinculados a um clube oculto também saem das consultas do Matt Scout; o save original não é alterado.

Categoria desconhecida continua visível. Não ter jogadores lidos, ter reputação baixa ou repetir um nome não determina gênero. A referência não cobre todos os 33.884 registros do save nem clubes adicionados por bases personalizadas, portanto não certifica que todo registro feminino tenha sido identificado. Clubes sem jogadores lidos mostram “Nenhum jogador lido” na tabela e no perfil de elenco.

## Área e função do staff

As listas `Staff.list_indexes` permitem identificar áreas: 0 médica, 1 comissão técnica e 2 recrutamento. A ordem foi documentada no [leitor gilet, seção das listas de staff](https://github.com/fifteen15-labs/gilet/blob/main/docs/SAVE_FORMAT.md). Ela organiza o filtro e a coluna Área do staff; uma pessoa pode aparecer em mais de uma lista. Ausência de lista resulta em Área não identificada.

O campo Função identifica Treinador (humano) pelo leitor, e Treinador principal/Diretor de futebol pelos assentos decodificados experimentalmente e contrato no mesmo clube. Os demais exibem Cargo não identificado; filtros de cargo e área são separados. Fontes em `STAFF_ROLES_RESEARCH.md`. Os títulos exatos, como olheiro, auxiliar, fisioterapeuta ou preparador, não foram deduzidos da área nem do código `unknown.r4`: o próprio fmsave documenta que esse código não corresponde ao cargo.

Soma de habilidades usa as 19 competências profissionais decodificadas pelo adaptador experimental `staff_skills.py`, sem preferências de estilo ou personalidade. Um componente ausente deixa a soma indisponível. Fontes, validação estrutural e limites estão em `STAFF_READER_RESEARCH.md`.
