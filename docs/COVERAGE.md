# Cobertura da especificação · versão 0.1

Esta versão lê saves reais. Ainda não é equivalente funcionalmente ao Genie Scout. “Funcional” indica o comportamento implementado; não certifica campos que o próprio leitor classifica como não confirmados.

## Jogadores: pesquisa e perfil

| Grupo solicitado | Situação |
|---|---|
| Nome; idade mínima/máxima; clube | Funcional. Busca sem diferenciar acentos. Clube inclui todas as equipes vinculadas por padrão. |
| Nacionalidade; país onde atua | Nomes em português, busca e seleção múltipla. Nacionalidade considera a principal e todas as adicionais lidas, listadas no perfil e na coluna. Mapa com 228 países/federações; códigos não mapeados ficam fora das opções. País onde atua continua ligado ao clube, não às cidadanias. |
| Região da nacionalidade; região onde atua | Funcional com busca, seleção múltipla e persistência nos filtros. Região da nacionalidade considera todas as cidadanias lidas. Região onde atua usa o país da liga do clube; sem vínculo identificado, não há correspondência regional. |
| União Europeia | Funcional: basta uma das nacionalidades lidas pertencer aos 27 membros atuais. Perfil, coluna e filtro Sim/Não/Qualquer. País não mapeado sem cidadania UE conhecida resulta em Indisponível e não passa pelo filtro Não. Não calcula regras de inscrição ou tratados adicionais de uma competição. |
| Regen | Pendente. Não inferir pela faixa de ID. |
| Internacionalizações e gols pela seleção | Pendente. |
| Liga do clube | Pendente: o leitor não oferece vínculo confiável com a divisão atual do clube. O controle fica desabilitado. Tabelas de copas/fases não são tratadas como liga; nomear uma competição não prova que ela seja a liga atual de um clube. |
| Posição em campo e posições secundárias | Funcional. Campo clicável; familiaridade mínima 15. Perfil mostra valores 1–20 e pés. |
| CA/PA mín./máx.; PA − CA | Funcional sobre campos experimentais do leitor, com ressalva †. |
| Rating atual | Estimativa própria da melhor posição familiar. Fórmula/coeficientes no perfil. |
| Rating potencial; progress rate; probability of development; projeções | Pendente. Não simular uma projeção sem modelo validado. |
| Reputação nacional/atual/mundial; reputação do clube | Filtros de intervalo funcionais nos campos presentes. |
| Reputação do elenco | Pendente. O bucket de reputação não foi tratado como esse campo. |
| Somente na shortlist | Funcional. |
| Situação de contrato; sem contrato | Parcial: filtra ausência de contrato **decodificado**. Ausência não prova liberdade contratual. |
| Expiração contratual em período | Funcional, de/até, inclusivo. |
| Regra Bosman | Pendente. Não universalizar prazo/regra. |
| Tipo de contrato; status no elenco | Funcional para opções nomeadas pelo leitor; códigos sem nome não são oferecidos na pesquisa. |
| Transferência/empréstimo listado; disponibilidade; interessados e relações | Pendente. Empréstimo existente é mostrado quando decodificado. |
| Valor de mercado; salário | Valor de mercado nas unidades do save. Salário com moeda/período configuráveis, padrão EUR/mês; conversão conferida por carreira/moeda usando um salário exibido no FM. Até conferir, permanece identificado como bruto semanal. Filtro salarial convertido para a unidade semanal original, preservado ao trocar a exibição. Referência arredondada dá estimativa; campo do leitor permanece experimental. |
| Valor estimado de venda | Pendente. |
| Cláusulas gerais/domésticas/estrangeiras, rebaixamento/não promoção | Funcional nas cláusulas nomeadas pelo leitor. Perfil mostra valores e condições brutas. Valor do filtro é a menor cláusula de liberação presente e pode ser condicional. |
| Técnicos (14); mentais (14); físicos (8) | Funcional: mínimos e máximos por atributo, inclusive. |
| Ocultos (5); personalidade (8) | Funcional: mínimos/máximos. Campos como lesões e controvérsia aceitam limites superiores. |
| Goleiro (11) | Funcional: mínimos/máximos e soma específica. |
| Traits | Parcial: pesquisa por 16 nomes confirmados pelo leitor; condições combinadas com AND. Movimentos ainda sem nome não são oferecidos como IDs. |
| Soma solicitada pelo usuário | Funcional: 36 atributos de linha, sem ocultos/personalidade/CA/PA/goleiro. Total ausente quando algum componente falta. |
| Foto; peso | Pendentes. Não foram inventados ou obtidos de packs externos. |
| Altura; pés; nascimento; ID | Altura em cm no perfil e como coluna ordenável, com filtros mínimo/máximo salvos. Campo experimental do leitor. Pés, nascimento e ID no perfil. Peso em kg sem decoder confiável. |
| Condição e ritmo | Valores brutos do save no perfil. Percentuais, fadiga e lesões atuais detalhadas pendentes. |
| Relatório | Maiores/menores atributos e melhor nota estimada entre posições familiares. Sem parecer gerado por IA. |
| Evolução | Snapshots das datas abertas neste caminho, com CA/PA e soma. Não reconstrói o passado. |

## Staff

Busca por nome, clube, idade, nacionalidade pelo nome, regiões, cidadania UE, CA/PA e personalidade. Staff atualmente tem apenas a nacionalidade principal disponível no leitor. Salário e expiração disponíveis quando lidos. Perfil mostra as preferências de estilo que o leitor conhece: ataque, negócios, passes diretos, interferência, paciência, pressão, recursos, compra de jogadores, jogos psicológicos, flexibilidade, intensidade de treino, rotação, ritmo e largura. **Preferências não são capacidade de treinamento.**

Colunas Função e Área do staff e filtro de área com busca/seleção múltipla: médica, comissão técnica e recrutamento vêm das listas do clube. A função exata só é identificada para o treinador humano; os demais mostram Cargo não identificado. 19 habilidades profissionais têm colunas, filtros mínimo/máximo, perfil e comparação. A soma das 19 tem máximo 380 e fica ausente se algum componente faltar; preferências e personalidade ficam fora. Leitura experimental, com fontes e limites em `STAFF_READER_RESEARCH.md`. Detalhes em `CLUB_GENDERS.md`.

Pendentes: demais cargos atuais confiáveis, gênero das pessoas, regen, nacionalidades adicionais do staff, regras específicas de elegibilidade, reputações próprias, best rating, estrelas/ratings de treino, trabalho com jovens, disciplina e pesquisa por cargo específico de especialistas em bolas paradas. Motivação, avaliação de capacidade/potencial, fisioterapia, conhecimento tático, gestão e treino de bolas paradas já são lidos experimentalmente. Não há base suficiente para recomendar os melhores olheiros ou treinadores por esses atributos nesta versão.

## Clubes

| Grupo solicitado | Situação |
|---|---|
| Nome; país; divisão; reputação | Nome/reputação e país pelo nome funcionais. Liga atual pendente. |
| Saldo; transferências restantes; orçamento salarial | Perfil, filtros e colunas ordenáveis nos clubes com dados financeiros decodificados. Data exposta no perfil. Saldo/transferências nas unidades do save; orçamento salarial usa a configuração de moeda/período dos salários. |
| Médias CA/PA/idade; número de jogadores | Funcional, ordenável, cobertura por indicador. Equipe principal ou todos os vinculados. |
| Base/reservas | Incluídas em Todos, quando vinculadas pelo leitor. Os nomes exatos das categorias secundárias estão pendentes. |
| Masculino/feminino | Femininos identificados por referência local de IDs são ocultados; 1.017 no COR. Masculinos conhecidos e categoria desconhecida permanecem. Sem classificação por nome, faixa de ID ou ausência de elenco. Cobertura parcial, documentada em `CLUB_GENDERS.md`. |
| Ausência de elenco lido | Mostra Nenhum jogador lido em vez de 0 na tabela e no perfil; não afirma que o clube esteja sem elenco no jogo. |
| Formação, treino e academia | Pendente. Instalações corporativas não foram confundidas com treino/formação. |
| Estádio | Lugares sentados e capacidade de expansão em perfil, colunas e filtros; vínculo pelos jogos em casa somente se houver um estádio único. Propriedade não é usada como vínculo. Nome não lido no COR; não substituído por ID. Capacidade total e público médio/mín./máx. pendentes. |
| Status profissional/semiprofissional/amador; uniformes | Pendente. |
| Elenco | Perfil com médias e link para pesquisar todos os jogadores do clube. |
| Desempenho por formação e top 5 formações | Pendente. |

## Organização e interoperabilidade

| Função | Situação |
|---|---|
| Ordenação e atributos como colunas | Funcional. |
| Colunas personalizadas e layout persistente | Funcional por tipo de lista, também acessível pelo botão direito no cabeçalho. |
| Comparação | Funcional, dois registros de jogadores ou staff. Resumo no topo com atributos vencidos, empates e dados ausentes; vencedor destacado em verde e texto. Jogadores de linha e comparação mista usam 36 atributos técnicos/mentais/físicos, sem seção ou destaque de goleiro. Se ambos têm familiaridade GK ≥15, os 11 de goleiro entram na tabela e no placar, totalizando 47. Pesos iguais; idade, CA/PA, soma, ocultos e personalidade ficam fora do placar dos jogadores. Staff conta as 19 habilidades profissionais com pesos iguais; personalidade aparece separada e fica fora do placar. |
| Listas | Persistência local, CSV básico e JSON portátil. Importação compara ID, nome e nascimento. |
| Shortlist `.fmf` importável no FM | Pendente: exige implementação/validação do formato real e um roundtrip no jogo. |
| Busca do clube do treinador | Funcional quando o leitor identifica o treinador/clube. |
| Busca de elenco de seleção nacional | Pendente. Não confundir todos os jogadores de uma nacionalidade com convocados. |
| Filtros combinados e filtros táticos salvos | Funcional. JSON validado e importação sem substituição dos filtros existentes. |
| Busca interna e seleção múltipla | Clube, todas as nacionalidades lidas, país onde atua, regiões, tipo de contrato, status no elenco e cláusulas. Campo permite múltiplas posições. OR no mesmo campo; AND entre campos. Liga atual ainda pendente. |
| Mais linhas na lista | Carregar mais acrescenta 50/100/200 linhas; conserva registros carregados e posição da rolagem, com indicação de fim. Filtros/ordenação/colunas reiniciam a lista. |
| Número da linha | Coluna Nº fixa à esquerda para jogadores, staff e clubes. Segue filtros/ordenação, continua ao carregar mais e reinicia com uma nova pesquisa. |
| Avaliação por Jev/OpenJev | Adiada por decisão do usuário. Nenhum modelo instalado ou dados enviados a esses serviços. |
| Instalador autônomo/notarização | Pendente. O `.app` local depende da `.venv` do projeto. |

## Próxima dependência concreta

Ampliar/confirmar a decodificação do FM26. O maior limite está nos dados, especialmente staff, países/competições, inscrições em seleções, estados de transferência e projeções. Uma interface habilitada sem dados confiáveis não resolve esses itens. Validar cada novo campo contra o mesmo jogador/profissional/clube e a mesma data do save antes de marcá-lo como confirmado.
