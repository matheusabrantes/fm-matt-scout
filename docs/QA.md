# Validação · 12/10/2026

## Dados reais

`qa/check_save.py` leu **Matheus Abrantes - COR.fm**, FM26 `26.3.2+2329565`, data no jogo 29/12/2025. Resultado: 63.514 jogadores, 10.389 membros do staff e 33.884 clubes; nenhum aviso dos leitores utilizados. A última execução levou 21,25 segundos neste Mac.

O hash SHA-256 do arquivo original foi comparado antes/depois e permaneceu igual. A leitura acontece em uma cópia temporária. O teste também verificou rejeição de acesso HTTP sem token, soma dos 36 atributos contra o perfil, persistência/importação da lista, roundtrip dos filtros, colunas/ordenabilidade por atributo e preservação do save anterior após abrir um arquivo inválido.

Corinthians: 28 jogadores no vínculo principal, 28 valores disponíveis para cada média. CA médio 125,5714; PA médio 137,7143; idade média 27,3214. Isso comprova os cálculos sobre os campos extraídos, **não** uma confirmação independente de CA/PA ou da classificação de equipes.

O mesmo teste passou também no save **Matheus Abrantes - Brasil.fm**: 60.532 jogadores, 10.023 membros do staff e 33.841 clubes, mesma build e data no jogo, sem avisos; original preservado. Execução de 19,82 segundos.

## Lógica

20 testes passaram em `qa/test_scout.py`: limites/soma exata e ausência de atributos; desempate; filtros combinados e intervalos inclusivos; acentos; PA ausente na ordenação; atributos como colunas; médias/cobertura; inclusão de equipes secundárias; cláusulas/traits; escolhas múltiplas com OR/AND; validação e importação atômica de filtros; nomes de países e ordenação alfabética; regiões da nacionalidade e do clube independentes; nacionalidades adicionais no filtro de país, região e UE. País não identificado não passa como Não UE; formação no país não vira cidadania. O filtro de liga não aceita vínculos de copa como divisão.

Mais 3 testes em `qa/test_salaries.py` passaram (23 no total): padrão EUR/mês sem taxa inventada; conversão por referência, moeda e carreira, persistida; rejeição de referência inválida sem sobrescrever preferências.

## Interface

`qa/check_ui.cjs` passou em 17 fluxos, com zero erros de console, usando Chromium neste Mac e storage temporário isolado:

1. Carregar o save COR pela interface.
2. Ordenar pela soma e consultar totais por categoria.
3. Abrir atributos, ocultos, contrato, posições, relatório e evolução.
4. Comparar dois jogadores: placar no topo, vencedor em verde e texto, empate e ausência de dados. Fixtures conferiram vitória de cada lado, empate com 35 atributos iguais e um ausente, dois goleiros e comparação mista. A seção Goleiro fica ausente em jogadores de linha e comparação mista, sem destaque ou contagem; dois goleiros contam 47 atributos. Idade e CA favoráveis ao perdedor não alteram o placar.
5. Selecionar múltiplas posições; pesquisar Brasil/Portugal pelos nomes e selecionar ambos; confirmar que buscar o código interno não oferece uma opção; filtrar país, regiões da nacionalidade e onde atua, clube, idade, atributos, contrato e traits. Confirmar filtro de liga desabilitado por falta do vínculo atual e ausência do campo de busca por IDs de movimentos.
6. Salvar/exportar/restaurar/importar/excluir filtros.
7. Abrir colunas pelo clique direito no cabeçalho, acrescentar Passe, remover Idade, ordenar por atributo e persistir o layout.
8. Adicionar/remover/exportar/importar listas em CSV e JSON.
9. Consultar Meu time e o perfil de estilo do staff. Verificar colunas Função, Área do staff e Soma de habilidades; soma mostra Não disponível, sem substituir por personalidade/preferências. Filtro de áreas tem busca e seleção múltipla, com OR conferido por API; cargos exatos ausentes ficam explícitos.
10. Consultar/ordenar médias de clubes e alternar principal/todos.
11. Abrir o elenco do clube; alternar completo/principal/secundário; verificar botão desabilitado ao carregar todos os resultados.
12. Verificar ausência de overflow global em 1280, 1024, 850 e 390 px. A tabela rola em seu próprio contêiner.
13. Recarregar o save e reabrir a interface conservando a lista e o layout; Idade continua removida e Passe presente após inicializar novamente.
14. Encontrar um brasileiro com cidadania UE pelo país secundário, pelo filtro UE e no perfil.
15. Salários: EUR/mês padrão, referência sintética em storage temporário, mudança de período/moeda, conversão ausente explícita, limite salarial e persistência após recarregar.
16. Carregar mais: 100 → 200 → 250 jogadores, conservando os primeiros registros, sem duplicar IDs, com a mesma rolagem. Trocar a quantidade por clique e adicionar/remover um jogador da lista conserva as 250 linhas; limpar a busca reinicia com 100.
17. Conferir que Chelsea, Arsenal, Manchester City, Barcelona e Bayern permanecem com uma entrada homônima masculina após excluir os femininos identificados. Um clube real sem jogadores, servido isoladamente no teste de interface, mostra Nenhum jogador lido na tabela e no perfil. Numeração 1–250 foi verificada no carregamento cumulativo; staff e clubes começam em 1.

Mais dois testes Python passaram (25 no total): exclusão por ID de clube, preservando homônimos e categorias desconhecidas mesmo sem jogadores; áreas de staff, seleção múltipla validada, função desconhecida sem mapear `r4` e soma ausente. A leitura direta dos clubes do COR confirmou 33.884 originais, 1.017 identificados como femininos e 32.867 visíveis. A referência tem 1.499 IDs femininos e 40 masculinos conhecidos, sem inferir a categoria dos demais; ver `CLUB_GENDERS.md`.

Os testes abrangem os tipos de controle e fluxos listados; não clicam em cada opção de cada clube/nacionalidade, nem comparam todos os valores com o jogo. Capturas estão em `qa/jogadores.png`, `qa/comparacao.png`, `qa/filtros.png`, `qa/clubes.png` e `qa/mobile.png` (arquivos locais ignorados pelo Git). A captura da comparação real foi inspecionada: Declan Rice 19 atributos vencidos, Joshua Kimmich 13 e quatro empates, sem destaque na idade.

O detector visual de Impeccable não encontrou ocorrências nos arquivos HTML/CSS. Foco visível e números além das cores estão implementados; uma auditoria completa com leitores de tela não foi feita.

## macOS

O `.app` atualizado foi compilado com Swift/AppKit/WebKit e assinatura local e conferido no macOS após o desbloqueio. Carregou o save COR com 63.514 jogadores. A busca nativa por Vinícius Júnior mostrou “Brasil, Espanha” e “Sim” na coluna Nacionalidade UE; o perfil mostrou “Brasil (principal); Espanha · UE”. Os seletores por nome, seleção múltipla, seis regiões, campo de posições, Escape e painel Cmd+O foram conferidos nativamente antes da adição de salários. Limpar restaurou os 63.514 jogadores e o elenco Todos.

A árvore de acessibilidade fornecida pelo controle de interface mostrou poucos controles dentro dos diálogos HTML do WebKit. A conferência dos seletores usou screenshots e entrada nativa; não confirma cobertura completa com VoiceOver.

Na última versão, o contrato de Vinícius Júnior no `.app` mostrou “Salário · EUR / mês” e “€ 1.720.000”. O diálogo Salários abriu com Euro e Mensal selecionados e explicou a referência por carreira/moeda. Após essa execução, a assinatura continuou válida, sem caches Python acrescentados dentro do bundle.

A versão com carregamento cumulativo e placar também foi conferida no AppKit/WebKit: o botão acrescentou jogadores de 100 para 200 carregados; o clique direito no cabeçalho abriu “Colunas da tabela”. A comparação nativa de Lionel Messi com Kylian Mbappé mostrou 18 e 15 atributos vencidos e três empates, Messi destacado em verde e texto; idade sem destaque. A persistência de acrescentar/remover colunas foi verificada no teste Chromium isolado, incluindo reabertura da interface. App e ZIP foram comparados com as fontes atualizadas.

Na atualização seguinte, a tabela nativa de clubes mostrou a coluna Nº na ordem vigente, com linhas 42–52 visíveis após rolar e 100 resultados carregados. Total: 32.867 clubes, nota de 1.017 femininos identificados ocultos, 63.514 jogadores e 10.385 staff. O save COR original foi preservado. A numeração e os novos estados de ausência foram testados no Chromium nas três listas; a captura nativa confirmou a numeração e o resultado da exclusão na lista de clubes.

O usuário disponibilizou o FM aberto. Sua tela de dados pessoais de Vinícius Júnior, em 29/12/2025, confirmou “€ 1,72M p/m”, contrato até 30/06/2027 e nacionalidades Brasileiro/Espanhol. A conferência é de um jogador e de um salário abreviado; não confirma CA/PA nem todos os contratos. A navegação inicialmente retornou `noWindowsAvailable`; mesmo após disponibilizar o modo janela, não foi obtido um vínculo confiável para a liga atual. A investigação no FM foi interrompida a pedido do usuário para evitar o custo de memória/contexto; não houve alteração no jogo.

`codesign --verify --deep --strict` confirmou assinatura válida no disco; `plutil -lint` confirmou o Info.plist válido. O build remove metadados Finder dos arquivos gerados antes/depois da assinatura. A assinatura é local; isso não equivale a notarização para distribuição.

A execução do Python criou arquivos `__pycache__` dentro do `.app` assinado e a verificação após execução detectou os arquivos adicionados. O processo nativo agora passa `PYTHONDONTWRITEBYTECODE=1`; o build remove apenas esse cache gerado antes de assinar. A verificação deve ser feita também após abrir o aplicativo.

Na pasta do projeto, o provedor de arquivos recriou `com.apple.FinderInfo` após a limpeza e a verificação voltou a falhar. O build passou a gerar o `.app` em `~/Library/Application Support/FM Matt Scout/Application/` e um ZIP sem esses metadados em `dist/`. A cópia em Application Support é a entrega executável; a pasta antiga `dist/FM Matt Scout.app` pertence à instância anterior.

## Limites

Sem confirmação externa de CA/PA, validação de cada campo no jogo, importação `.fmf` no FM, teste em outro Mac, distribuição notarizada ou integração com Jev/OpenJev. A cobertura funcional detalhada está em `COVERAGE.md`.

## Gate da alteração visual

- Hard Gate PASS no escopo alterado: busca por nomes, opções conhecidas, estados de ausência explícitos, 17 fluxos sem erros de console e sem overflow nas quatro larguras testadas. O placar tem indicação textual além do verde existente; fixtures de teste não foram incorporadas ao aplicativo.
- Purpose Gate PASS: reutilizados os seletores existentes; nenhum efeito, ícone ou padrão decorativo adicionado.
- Liveliness PASS: mantida a direção de `DESIGN.md`, ENERGY 1 / RHYTHM 1 / MOTION 1, tabela como foco e campo como seleção de posições.
- Craftsmanship PASS no escopo alterado: código interno não é texto de busca; campos indisponíveis não simulam dados; 25 testes, build assinado localmente e 17 fluxos de interface. Conversão salarial exige referência por carreira e moeda. Categoria desconhecida não vira masculino/feminino por nome ou ausência de elenco; funções exatas e soma profissional de staff ficam explicitamente indisponíveis. VoiceOver completo e vínculo da liga atual continuam fora da cobertura confirmada.

## Habilidades profissionais, altura e estádio — 13/10/2026

30 testes Python passaram: validação de identidade/CA/PA/preferências/sentinel/limites dos bytes profissionais, rejeição de headers duplicados e humanos, conversão 1–100 para 1–20, composição das 19 competências, filtros/ordenação e teto 380, altura e associação do estádio pelos jogos em casa sem confundir propriedade.

20 fluxos Chromium passaram no COR, com zero erros de console. Além dos fluxos anteriores, foram exercitados perfil, filtro e comparação das competências profissionais; colunas financeiras/capacidades do clube; altura em cm como coluna ordenável e filtro. A API conferiu Nikolić com motivação 16, avaliação de capacidade/potencial 12/10, defesa 16 e soma 207, reproduzindo a referência externa descrita em `STAFF_READER_RESEARCH.md`. Metadados: 10.333 registros de staff com soma completa, de 10.385 visíveis. Corinthians: 48.905 lugares sentados e expansão 70.000. Layout e salários persistiram ao recarregar o save e a interface.

A soma profissional antes indisponível passou a usar 19 competências experimentais; personalidade continua separada. O FM aberto não foi usado. Não há confirmação visual no jogo na mesma data do save, nem cobertura de todos os atributos/cargos do staff. Peso, liga atual, treino/formação/academia permanecem pendentes.

A versão recompilada abriu o COR no aplicativo nativo e exibiu a coluna Soma de habilidades (19), Guardiola 250 e o campo Soma mín. com faixa 19–380. A API dessa instalação confirmou as mesmas contagens e os arquivos empacotados coincidem byte a byte com o código validado. SHA-256 do COR antes/depois da leitura nativa: `69c685db1ddd954386691909c987307440581f9b3621fb68825f7752fa8c89cc`. Assinatura `codesign --verify --deep --strict` e Info.plist válidos após executar o app. Assinatura local, sem notarização; pacote depende da .venv do projeto.

## Cargos por assento e ligas parciais — 13/10/2026

35 testes Python passaram e 22 fluxos Chromium passaram no COR, sem erros de console. Novos testes verificam truncamento dos assentos, selector/UID, contrato no clube correto, codificação UTF-8, sentinels e ambiguidades; seleção/salvamento de cargos; liga nacional nomeada somente para a equipe principal, sem copas/equipes secundárias e sem escolher entre dois vínculos. A interface exercitou cargo por nome com seleção múltipla, Guardiola como treinador principal e Marcelo Paz como diretor de futebol, liga Premier League propagada ao staff, filtro de clubes com 20 clubes e coluna Liga; Corinthians mostra Liga não lida.

Probe independente da integração, em cópia temporária do COR: 2.123 treinadores principais, 213 diretores de futebol, 1 treinador humano e 8.048 registros de cargo não identificado; 150 clubes com liga, em oito campeonatos. Soma profissional permanece disponível em 10.333 registros. O SHA-256 do original permaneceu igual antes/depois. Nomes das 56 divisões foram conferidos com a seção PT-BR do arquivo de idioma instalado. Nenhuma tela/processo do FM foi usado. Cargos/ligas permanecem experimentais e parciais; treino/base continuam indisponíveis.

O app nativo recompilado abriu COR e mostrou Treinador principal para Guardiola; a API da mesma instalação confirmou Premier League, 2.337 cargos identificados (inclui o treinador humano) e 150 clubes com liga. Os arquivos do app são idênticos ao código validado; assinatura `codesign --verify --deep --strict` e Info.plist válidos depois da execução. O SHA-256 do COR continua `69c685db1ddd954386691909c987307440581f9b3621fb68825f7752fa8c89cc`.

Revisão antislop durante a construção, no escopo desta alteração:

- Hard Gate PASS: captura local staff mostra nomes/cargos, ausência explícita e liga por nome; liga desconhecida do COR não é preenchida e os campos experimentais têm ressalva. Testes rejeitam liga de copa/equipe secundária e cargo de outro clube.
- Purpose Gate PASS: cargo e liga reutilizam os seletores pesquisáveis e a configuração de colunas existentes, para atender aos critérios de recrutamento pedidos; nenhuma decoração ou etapa nova.
- Liveliness PASS: direção visual 1/1/1 de DESIGN.md preservada, com tabela compacta, números alinhados e perfil lateral; captura staff revisada e testes sem overflow global de 390 a 1280 px.
- Craftsmanship PASS: 35 testes, 22 fluxos, zero erros de console, filtros por nome/seleção múltipla e layouts persistentes; aplicativo nativo assinado, save original preservado. Limites de cargo/liga e ausência de treino/base são documentados. VoiceOver completo e conferência no FM não foram exercitados.

## Atualização de 29–30/10/2026: oportunidades, cláusulas e cargos

Controle: COR de **30/12/2025**, build `26.3.2+2329565`, SHA-256
`7010e6db21345f51e2c1a4b00788e21994daae7ae998a271b9d75661f965e8a0`.
O original manteve esse SHA após a navegação somente de leitura no FM e a
compilação/instalação local. O `.app` foi atualizado no caminho canônico em
Aplicativos e recebeu assinatura local válida; recursos comparados com as fontes.

Os **55 testes Python** passaram, incluindo estados de contrato, desconhecidos
excluídos da busca de livres, prazos inclusivos por meses de calendário e ano
bissexto, datas heurísticas/futuras rejeitadas, estados de listagem 0/1/2 separados,
versões/estados desconhecidos indisponíveis, cláusulas gerais/nacionais/estrangeiras
sem agregar outras condições, ordenação com valores ausentes no fim e validação
dos filtros portáteis. Sintaxe de `web/app.js`, `qa/check_ui.cjs` e `build.command`
conferida. Os testes de cargos verificam propriedade, contrato vigente, ambiguidade
e prioridade de assentos, além de códigos desconhecidos mantidos sem rótulo.

Na execução nativa com o COR carregado: 63.514 jogadores, 10.537 staff, 32.867
clubes, nenhum aviso; **9.849 cargos identificados** e 10.479 somas profissionais
completas. As 25 categorias de cargo não cobrem todos os vínculos e não foram todas
conferidas em perfis do jogo. Nicolas Jover (bolas paradas), Raony e Toni Tapalović
(cargo atual de coordenação de análise de recrutamento) foram conferidos no FM;
a categoria profissional e o histórico não substituem o cargo atual exibido.

A API da instância nativa confirmou **8.607 livres, 12.635 com expiração em até
6 meses, 13.723 em até 12 meses, 302 listados para transferência e 1.281 para
empréstimo**. A listagem é parcial: 40.010 jogadores têm ambos os estados
identificados. O controle do FM mostrou Memphis Depay na lista de transferências,
Vitinho (32 anos) disponível para empréstimo e Yuri Alberto sem estatuto definido
em ambos. Os três resultados corresponderam à API. O botão nativo de transferências
mostrou 302 resultados e a busca Memphis Depay encontrou o jogador.

O contrato normal do FM confirmou a rescisão geral de Vinícius Júnior (€1 bilhão),
a nacional de Lucas Paquetá (€63M) e a de rebaixamento de Tiago Gabriel (€1M,
inativa enquanto a condição não ocorrer). Os tipos lidos correspondem; valores
brutos continuam em unidades do save, sem conversão monetária presumida.

Dívida atual dos clubes continua sem coluna: a investigação avançou nos registros
de prestações, mas proprietário estrutural e contador atual ainda não são
identificados com segurança. Ver `CLUB_DEBT_RESEARCH.md`. Não foi substituída
por dívida inicial, saldo ou estimativa extraída de capturas.

A execução final de `qa/check_ui.cjs`, encerrada em **30/10/2026**, passou em
**27 fluxos, com zero erros de console**, usando o Comet instalado como binário
Chromium e storage temporário isolado. Incluiu os cinco atalhos com conferência
da resposta e das linhas exibidas, ordenação nas três colunas de rescisão,
importação sem duplicação, comparação profissional do staff, tabelas de clubes,
quatro larguras de tela e recarregamento/reabertura preservando as três colunas.
O relatório local foi atualizado em `qa/local-ui-report.json` (ignorado no Git).
As esperas frágeis do teste foram ajustadas para aguardar os estados conferidos;
o HTML define ícone vazio para evitar pedidos sem a rota autorizada que geravam
403 no console. As fontes, recursos do app e arquivos correspondentes no ZIP
foram comparados byte a byte; assinatura e preservação do COR conferidas novamente.

## Correção monetária de 30/10/2026

**58 testes Python e 28 fluxos de interface passaram, com zero erros de console.**
A regressão nova percorre calibração por rescisão do perfil aberto, salário
preservado, mudança de período sem alterar rescisão, troca de moeda preservando
os limites, filtro salvo em unidade original e restauração na moeda atual.
Confere geral, nacional, estrangeira e rebaixamento, além da persistência da
referência após recarregar e reabrir. Entradas de calibração inválidas não
sobrescrevem preferências; referências de outra carreira/moeda não são herdadas.
Limites fracionários resultantes da conversão permanecem pesquisáveis.

No app nativo instalado, o COR mostrou **Vinícius Júnior com rescisão geral de
€1.000.000.000 e salário de €1.720.000/mês**, tanto na tabela quanto no perfil,
aba Contrato. A referência monetária foi salva localmente usando a cláusula do
mesmo save já conferida no FM; a taxa salarial e o período anteriores foram
preservados. Não há referência de jogador ou taxa fixa gravada no código.

A API instalada também confirmou os dois valores por cálculos independentes.
Os controles do teste de interface incluíram Paquetá (nacional), Tiago Gabriel
(rebaixamento) e um contrato com rescisão estrangeira. O FM abrevia valores e o
save armazena valores inteiros; essa conversão não certifica centavos de todas
as cláusulas. A pequena diferença no caso de Tiago está documentada em
`CONTRACT_READER.md`. Dívida atual e cargos restantes não mudaram nesta correção.

## Finanças atuais, euros e vínculos médicos — 30/10/2026

77 testes Python passaram e 32 fluxos Chromium passaram no COR, sem erros de console, incluindo recarregar o save e reabrir a interface. O teste monetário focado também passou. Filtros de valor de mercado, saldo e orçamento de transferências preservam unidades originais no JSON e o mesmo critério ao mudar moeda ou período; saldo negativo continua válido. O build inclui os dois novos leitores.

A conferência no FM identificou um erro de origem: o saldo anterior do Corinthians era um histórico mensal de 01/11/2025 (−€5.676.507), não o caixa atual. `club_finances.py` valida o prefixo da lista de patrocinadores dentro do registro próprio do clube e lê caixa, transferências e orçamento salarial atuais; quando não o reconhece, mantém o histórico com origem/data explícitas. O formato novo é limitado ao build 26.3.2+2329565. Controles independentes: caixa do COR €14.441.698; Real Madrid aproximadamente €137M e orçamento de transferências €50M. O probe encontrou 527 registros financeiros atuais antes da exclusão de clubes femininos.

A leitura de staff recuperou 57 registros de headers alocados e 629 vínculos médicos sem termos completos (315 diretores clínicos e 314 médicos). Os dados brutos de salário, datas e `has_contract` foram preservados; o vínculo atual é identificado separadamente e não entra na busca de staff livre. No conjunto bruto, 10.537 dos 10.541 registros têm cargo; os quatro restantes são contratos futuros. A tabela do FM confirmou Niko Mihić como Diretor clínico e Felipe Segura/Manuel Arroyo como Médicos, com nomes sem link, salário N/D e término N/A. Não houve conferência visual individual de todos os profissionais.

O novo leitor de empréstimos associa a lista ao clube pelo índice estrutural completo, sem mapear por nome ou valor coincidente. No conjunto bruto: 33.765 listas identificadas, 139 com empréstimos e 119 ausentes por ambiguidade. A aba Empréstimos mostra original, parcela, juros mensais, condições e datas, com a mesma moeda e sem fator salarial. Lista vazia não significa dívida líquida zero. COR mostra três vínculos Município; Real Madrid, dois vínculos Banco. Valores originais grandes podem diferir algumas unidades da tela do FM após a conversão; parcela e juros mensais dos controles ficaram a menos de €2. **O saldo restante e a fórmula da dívida líquida continuam não confirmados e não são estimados pelo app.**

A captura `qa/emprestimos.png` foi revisada: mantém a tabela densa, o perfil lateral, o aviso de indisponibilidade e os valores separados por significado. Foco e navegação usam os mesmos componentes existentes; nenhuma dependência ou decoração nova foi adicionada. Testes verificaram ausência de overflow global em 390, 850, 1024 e 1280 px.

A instalação canônica `/Applications/FM Matt Scout.app` foi atualizada, reaberta e conferida no AppKit/WebKit. O binário Swift permaneceu inalterado; os recursos Python/HTML/JS novos foram copiados, comparados às fontes e assinados novamente. App e ZIP contêm os leitores novos; assinatura e Info.plist válidos após executar. No perfil nativo do COR: caixa €14.441.698, verba €3.738.537, origem “Posição atual no save” e três empréstimos Município com original €122.878.822, parcela €608.909/mês e juros €330.902/mês. A busca nativa de Leandro Correia dos Santos mostrou Diretor clínico no Corinthians. A API dessa instalação confirmou 10.533 cargos em 10.537 staff visíveis e 10.536 somas profissionais completas. Layouts e calibração monetária mantiveram o mesmo hash; o COR original continuou com SHA-256 `3795481a7bebcdd4512f3c1419b3c0890adda042dc1f5fa74cb73b92874cde8d` após as leituras e a execução nativa.


## Liga atual, estádio e atributos profissionais — 30/10/2026

90 testes Python e o teste monetário com o JavaScript real passaram. O teste da coluna de estádio reproduziu NaN antes da correção e passou depois; também cobre valor zero no perfil contratual. Os novos testes rejeitam status de outro clube, cabeçalhos duplicados/truncados, formatos desconhecidos e nomes inválidos, preservam lacunas de IDs de estádios e impedem que uma copa preencha a liga ausente. A coluna Determinação continua usando a origem correta em jogadores e staff.

33 fluxos Chromium passaram, sem erros de console, com leitura/releitura do COR, persistência e quatro larguras de tela. A primeira execução parou em um seletor antigo que ainda esperava “19”; o log foi mantido, corrigido para “21” e a execução seguinte terminou. Novos fluxos conferem os quatro atributos de Célio, soma ativa, ausência de verde/placar nos campos legados, liga atual do COR, nome do estádio e zero contratual distinto de jogador livre. Logs locais: `/tmp/fm-scout-ui-20261030-league-staff-values-01.log` e `-02.log`.

Conferências somente de leitura no FM: Célio Silva com Autoridade 17, Trabalho com jovens 15, Determinação 18 e Goleiros 1; Corinthians com Brasileirão - Série A e Neo Química Arena; Bayern com Bundesliga e Allianz-Arena; Madrid com La Liga Santander e Santiago Bernabéu. Vítor Manoel mostrou €0 e contrato até 28/02/2026. Harry Kane mostrou Não está à venda; seu sentinela de 300 milhões não foi convertido em dinheiro. Não houve proposta, modificação de contrato ou avanço do jogo pela tarefa.

As novas somas usam 21 competências ativas, máximo 420. Dois campos antigos de goleiros permanecem nomeados como legado para preservar filtros/layouts, fora da soma e do placar. Nomes de liga/estádio usam a instalação local; alterações de nome sem string no save podem permanecer com o nome da base instalada. Nem todos os bytes do editor foram decodificados; não foi implementado modelo de preço de compra sem validação.

A instalação `/Applications/FM Matt Scout.app` e o ZIP foram atualizados sem reinstalar dependências nem recompilar a interface nativa. Fontes e recursos no bundle/ZIP são idênticos aos validados; Info.plist e assinatura ad hoc passaram após executar. No AppKit/WebKit, a busca do Corinthians mostrou Brasileirão e o perfil Neo Química Arena; Célio mostrou os quatro novos atributos conferidos e soma 156, com limite 21–420 na interface. A API da instalação confirmou 25.593 clubes com liga, 10.536 somas de staff e Vítor Manoel com valor 0/contratado. Layouts e calibração monetária mantiveram os hashes capturados no início da atualização. O COR original manteve SHA-256 `3795481a7bebcdd4512f3c1419b3c0890adda042dc1f5fa74cb73b92874cde8d`.
