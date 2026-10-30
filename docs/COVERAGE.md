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
| Liga do clube | Vínculo pela liga atual no status do próprio clube, com nomes da instalação local do FM. Filtro pesquisável/múltiplo, perfil e coluna nas três listas. Tabelas de divisões nacionais são alternativa limitada; copas não preenchem lacunas. Corinthians agora tem Brasileirão. Cobertura ainda parcial; detalhes em `LEAGUES.md`. |
| Posição em campo e posições secundárias | Funcional. Campo clicável; familiaridade mínima 15. Perfil mostra valores 1–20 e pés. |
| CA/PA mín./máx.; PA − CA | Funcional sobre campos experimentais do leitor, com ressalva †. |
| Rating atual | Estimativa própria da melhor posição familiar. Fórmula/coeficientes no perfil. |
| Rating potencial; progress rate; probability of development; projeções | Pendente. Não simular uma projeção sem modelo validado. |
| Reputação nacional/atual/mundial; reputação do clube | Filtros de intervalo funcionais nos campos presentes. |
| Reputação do elenco | Pendente. O bucket de reputação não foi tratado como esse campo. |
| Somente na shortlist | Funcional. |
| Situação de contrato; sem contrato | Atalho Sem contrato usa ausência explícita de registro e termos contratuais atuais; objetos de contrato vazios ou leitura incompleta não são confundidos com liberdade contratual. Perfil distingue livre, contratado e não identificado. |
| Expiração contratual em período | Funcional, de/até, inclusivo. Atalhos de 6/12 meses usam a data da carreira e meses de calendário, com contrato atual e data de expiração de fonte contratual; excluem vencidos e datas heurísticas. |
| Regra Bosman | Pendente. Não universalizar prazo/regra. |
| Tipo de contrato; status no elenco | Funcional para opções nomeadas pelo leitor; códigos sem nome não são oferecidos na pesquisa. |
| Transferência/empréstimo listado; disponibilidade; interessados e relações | Atalhos de lista de transferências/empréstimos e estados no perfil, experimentais no build 26.3.2. Códigos 0/1/2 conferidos no FM; combinações e estados desconhecidos ficam fora. Estar emprestado não implica estar listado. Disponibilidade geral, interessados e relações seguem pendentes. |
| Valor de mercado; salário | Valor zero explícito preservado sem implicar ausência de contrato; sentinelas permanecem indisponíveis com motivo no perfil. Valor de mercado convertido na tabela, perfil e filtros pela configuração de moeda, sem fator de período salarial. Salário com moeda/período configuráveis, padrão EUR/mês; conversão conferida por carreira/moeda usando um salário exibido no FM. Até conferir, permanece identificado como bruto semanal. Filtro salarial convertido para a unidade semanal original, preservado ao trocar a exibição. Referência arredondada dá estimativa; campo do leitor permanece experimental. |
| Valor para scout e compra estimada | Modelo experimental FMSuperScout, versão fixa, independente do campo original. Colunas ordenáveis/configuráveis, filtros portáteis e perfil com origem/faixas. Valor positivo do save prioritário; regressão nas lacunas. Preço efetivamente aceito continua sem leitura/validação. A regressão pura ficou dentro de 1/8 faixas dos controles COR/Madrid; não equivale à faixa do FM. Detalhes em `PLAYER_VALUES_RESEARCH.md`. |
| Cláusulas gerais/domésticas/estrangeiras, rebaixamento/não promoção | Colunas configuráveis Rescisão geral, nacional e internacional são ordenáveis e preservadas no layout. Cada uma usa exclusivamente o tipo correspondente sem parâmetro adicional; divisão superior e rebaixamento não são agregados. Perfil traduz as condições, como rebaixamento e não promoção. Filtro por tipo usa o menor valor entre os tipos selecionados. Tabela, perfil e limites de busca convertidos para a moeda selecionada, com referência própria de rescisão por carreira/moeda. Não recebe fator de período salarial. Fallback da taxa salarial identificado como aproximado; sem taxa, unidades do save explícitas. Filtros portáteis preservam limites originais. |
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

Colunas Função e Área do staff e filtro de área com busca/seleção múltipla: médica, comissão técnica e recrutamento vêm das listas do clube. Cargos atuais também são lidos pelo contrato vigente, com propriedade de pessoa/clube/equipe e termos conferidos. Assentos identificam treinador principal e diretor de futebol, com prioridade sobre funções acumuladas. Inclui filtro de cargo com busca/seleção múltipla e persistência. Contratos incompletos, ambíguos ou sem código demonstrado mostram Cargo não identificado. O treinador humano continua explicitamente identificado. Fontes/limites em `STAFF_ROLES_RESEARCH.md`. 23 campos profissionais têm colunas, filtros mínimo/máximo, perfil e comparação. A soma de 21 competências ativas tem máximo 420; os dois campos antigos de goleiro são marcados como legado e ficam fora da soma/placar. A soma e fica ausente se algum componente faltar; preferências e personalidade ficam fora. Leitura experimental, com fontes e limites em `STAFF_READER_RESEARCH.md`. Detalhes em `CLUB_GENDERS.md`.

Vínculos médicos sem termos completos também identificam Médico e Diretor clínico, sem inventar salário ou término; não entram na busca de staff livre. Pendentes: contratos futuros ou vínculos sem formato demonstrável, gênero das pessoas, regen, nacionalidades adicionais do staff, regras específicas de elegibilidade, reputações próprias, best rating, estrelas/ratings de treino, ratings por especialidade. Preparador de bolas paradas está disponível como cargo e filtro. Motivação, avaliação de capacidade/potencial, fisioterapia, conhecimento tático, gestão e treino de bolas paradas já são lidos experimentalmente. Não há base suficiente para recomendar os melhores olheiros ou treinadores por esses atributos nesta versão.

## Clubes

| Grupo solicitado | Situação |
|---|---|
| Nome; país; divisão; reputação | Nome/reputação e país funcionais. Liga com cobertura parcial pela tabela, descrita acima. |
| Dívida atual | Total líquido ainda sem decoder seguro. A aba Empréstimos mostra listas atuais identificadas por clube, valores originais, parcela e juros mensais e datas em moeda configurada. Lista vazia não significa dívida líquida zero. A conferência no FM e os avanços na estrutura dos empréstimos estão em `CLUB_DEBT_RESEARCH.md`; saldo e principal original não substituem dívida atual. |
| Saldo; transferências restantes; orçamento salarial | Perfil, filtros e colunas ordenáveis nos clubes com dados financeiros decodificados. Posição atual do save quando o prefixo financeiro é validado; histórico mensal como fallback, com origem e data expostas no perfil. Saldo e transferências usam a moeda selecionada sem fator salarial; valores negativos, limites de busca e filtros salvos preservam as unidades originais. Orçamento salarial usa a configuração de moeda/período dos salários. |
| Médias CA/PA/idade; número de jogadores | Funcional, ordenável, cobertura por indicador. Equipe principal ou todos os vinculados. |
| Base/reservas | Incluídas em Todos, quando vinculadas pelo leitor. Os nomes exatos das categorias secundárias estão pendentes. |
| Masculino/feminino | Femininos identificados por referência local de IDs são ocultados; 1.017 no COR. Masculinos conhecidos e categoria desconhecida permanecem. Sem classificação por nome, faixa de ID ou ausência de elenco. Cobertura parcial, documentada em `CLUB_GENDERS.md`. |
| Ausência de elenco lido | Mostra Nenhum jogador lido em vez de 0 na tabela e no perfil; não afirma que o clube esteja sem elenco no jogo. |
| Formação, treino e academia | Pendente. Instalações corporativas não foram confundidas com treino/formação. |
| Estádio | Lugares sentados e capacidade de expansão em perfil, colunas e filtros; vínculo atual no status do clube, com jogos em casa como alternativa somente se houver um estádio único. Propriedade não é usada como vínculo. Nome pelo vínculo atual e pela base local do FM; Neo Química Arena lida no COR. Coluna de nome configurável. Capacidade total e público médio/mín./máx. pendentes. |
| Status profissional/semiprofissional/amador; uniformes | Pendente. |
| Elenco | Perfil com médias e link para pesquisar todos os jogadores do clube. |
| Desempenho por formação e top 5 formações | Pendente. |

## Organização e interoperabilidade

| Função | Situação |
|---|---|
| Ordenação e atributos como colunas | Funcional. |
| Colunas personalizadas e layout persistente | Funcional por tipo de lista, também acessível pelo botão direito no cabeçalho. |
| Comparação | Funcional, dois registros de jogadores ou staff. Resumo no topo com atributos vencidos, empates e dados ausentes; vencedor destacado em verde e texto. Jogadores de linha e comparação mista usam 36 atributos técnicos/mentais/físicos, sem seção ou destaque de goleiro. Se ambos têm familiaridade GK ≥15, os 11 de goleiro entram na tabela e no placar, totalizando 47. Pesos iguais; idade, CA/PA, soma, ocultos e personalidade ficam fora do placar dos jogadores. Staff conta as 21 competências profissionais ativas com pesos iguais; personalidade aparece separada e fica fora do placar. |
| Listas | Persistência local, CSV básico e JSON portátil. Importação compara ID, nome e nascimento. |
| Shortlist `.fmf` importável no FM | Pendente: exige implementação/validação do formato real e um roundtrip no jogo. |
| Busca do clube do treinador | Funcional quando o leitor identifica o treinador/clube. |
| Busca de elenco de seleção nacional | Pendente. Não confundir todos os jogadores de uma nacionalidade com convocados. |
| Filtros combinados e filtros táticos salvos | Funcional. JSON validado e importação sem substituição dos filtros existentes. |
| Busca interna e seleção múltipla | Clube, todas as nacionalidades lidas, país onde atua, regiões, tipo de contrato, status no elenco e cláusulas. Campo permite múltiplas posições. OR no mesmo campo; AND entre campos. Liga tem cobertura parcial pelas tabelas; cargo do staff inclui treinador/diretor identificados e desconhecidos. |
| Mais linhas na lista | Carregar mais acrescenta 50/100/200 linhas; conserva registros carregados e posição da rolagem, com indicação de fim. Filtros/ordenação/colunas reiniciam a lista. |
| Número da linha | Coluna Nº fixa à esquerda para jogadores, staff e clubes. Segue filtros/ordenação, continua ao carregar mais e reinicia com uma nova pesquisa. |
| Avaliação por Jev/OpenJev | Adiada por decisão do usuário. Nenhum modelo instalado ou dados enviados a esses serviços. |
| Instalador autônomo/notarização | Pendente. O `.app` local depende da `.venv` do projeto. |

## Próxima dependência concreta

Ampliar/confirmar a decodificação do FM26. O maior limite está nos dados, especialmente staff, países/competições, inscrições em seleções, estados de transferência e projeções. Uma interface habilitada sem dados confiáveis não resolve esses itens. Validar cada novo campo contra o mesmo jogador/profissional/clube e a mesma data do save antes de marcá-lo como confirmado.
