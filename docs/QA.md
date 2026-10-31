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


## Estimativas FMSuperScout — 30/10/2026

Controles em `qa/fixtures/value-model-controls.json` registram oito faixas
observadas no FM aberto, cinco jogadores do Corinthians e três do Madrid.
O campo positivo do save ficou dentro de 8/8 faixas; a regressão pura, 1/8.
Não foi negociada transferência nem alterado o save. Isso não valida preço aceito
ou acurácia da regressão para valores ausentes. Detalhes e desvios em
`PLAYER_VALUES_RESEARCH.md`.

98 testes Python passaram. Novos casos cobrem resultado numérico da versão fixa,
prioridade do campo lido, zero preservado, prazo curto/default, contratos futuros
mesmo sem expiração lida, campos inválidos, salário relativo com empates, listagem
e filtros portáteis. Um valor esperado do teste de contrato curto foi corrigido
de 25,9 para 26,2 milhões após cálculo independente em JavaScript; a implementação
já produzia 26,2. O teste monetário executa o JavaScript real e confere campos do
modelo na tabela/perfil, marca ≈, conversão, filtros e independência de período.

34 fluxos Chromium passaram com zero erros de console, incluindo leitura e
releitura do COR, persistência e quatro larguras de tela. O fluxo novo verifica
colunas do modelo, valor original prioritário de Vinícius, fallback separado de
Kane, compra em EUR no perfil/coluna e limite monetário salvo na unidade original.
Log local: `/tmp/fm-scout-ui-20261030-value-model-01.log`.

Recursos da instalação e ZIP atualizados sem reinstalar dependências/recompilar
Swift; conteúdo comparado com os fontes e assinatura ad hoc verificada.

A instalação AppKit/WebKit carregou 63.514 jogadores, 10.537 staff e 32.867
clubes. O perfil contratual de Hugo Souza mostrou valor para scout €10.124.522,
origem Lido do save, compra estimada ≈€14.348.418 e os dois intervalos do modelo.
Isso confirma a apresentação/cálculo na instalação, não um preço de transferência
validado no FM. Um texto antigo do rodapé foi corrigido para distinguir preço
aceito de estimativa; o teste JavaScript verifica a nova redação.
Layouts/calibração monetária e COR original mantiveram os hashes anteriores.


## Colunas financeiras padrão — 30/10/2026

Valor de mercado agora usa `model_value` e aparece ao lado do clube, seguido de
Compra estimada (`model_fee`). Valor bruto continua opcional como Valor lido do
save, sem alterar os dados ou as fórmulas. Layouts sem versão migram uma vez:
remove a coluna bruta da visualização padrão, insere as duas combinadas e
preserva a ordem relativa das demais colunas e as listas de staff/clubes.
O marcador interno não é exposto pela API. Escolhas salvas depois da migração
continuam válidas, inclusive remover as novas colunas ou selecionar o valor bruto.

104 testes Python passaram, incluindo seis novos controles de layouts: ausência
de arquivo, migração idempotente, layout mínimo, preferência posterior,
recusa de formato/versão inválidos sem reescrever o arquivo e GET/POST HTTP real
com rejeição de coluna inválida. O teste JavaScript real verificou defaults,
nomes e apresentação de valores/estimativas. A suíte Chromium de 34 fluxos foi
executada na etapa anterior do modelo; não foi repetida para esta mudança de
padrões. Nenhuma fórmula monetária foi alterada.

A configuração deste Mac migrou automaticamente; staff/clubes e calibração
monetária foram preservados. Cópia anterior do layout mantida localmente em
`/tmp/fm-scout-layout-before-market-defaults-20261030.json`.

A instalação atualizada foi aberta e carregou o COR. A tabela nativa mostrou
Valor de mercado · EUR e Compra estimada · EUR imediatamente após Clube, sem
seleção manual de colunas. Messi/Kane passaram a mostrar estimativas com ≈,
enquanto o valor lido de Mbappé permaneceu sem essa marca. Não há coluna bruta
na visualização padrão. Bundle/ZIP e assinatura local conferidos novamente.


## Ordem lógica das colunas — 30/10/2026

Uma definição de grupos compartilhada na API orienta tabela, seletor e ordem
salva de jogadores, staff e clubes. A migração de layouts para versão 2
reorganiza as seleções existentes; não reativa campos que o usuário removeu
após a primeira migração financeira. Valores desconhecidos da definição ficam
no fim, preservando sua ordem relativa e disponíveis no seletor. Grupos do staff
separam gestão/liderança, treinamento, recrutamento, saúde, legado e personalidade.
Cabeçalhos textuais passam a alinhar com suas células.

106 testes Python e o teste JavaScript real passaram. Cobrem a migração nas três
listas sem mudar a seleção, idempotência, preservação de campos desconhecidos,
todos os atributos de staff sem duplicação, tabela e seletor com a mesma ordem,
e persistência via HTTP. Não houve mudança nos cálculos ou leitores do save.
A suíte completa Chromium não foi repetida para esta alteração de organização.

Na instalação AppKit/WebKit, o COR foi carregado e os cabeçalhos das três listas
foram conferidos: jogadores com identificação/vínculo antes de capacidade e
mercado; staff com idade/nacionalidade antes de função/área/clube; clubes com
liga antes de reputação, médias, finanças e estádio. O seletor do staff foi
inspecionado visualmente com categorias e seleções preservadas. A migração
manteve exatamente o conjunto de colunas de cada lista deste Mac; cópia anterior
em `/tmp/fm-scout-layout-before-logical-order-20261030.json`.


## Nomes curtos dos clubes — 30/10/2026

O staff agora recebe `club_short_name` pelo vínculo com o clube, como os jogadores.
A API da lista de clubes inclui `short_name`, usado no nome da tabela e no título
do perfil. Seletores e vínculo contratual preferem o nome curto. Nome completo
permanece nos detalhes/tooltips e é aceito na busca; ordenação por nome/clube segue
o texto exibido. Se faltar nome curto, mantém a alternativa de nome completo.

108 testes Python passaram. Novos controles cobrem busca pelos dois nomes e
ordenação pelo nome curto em clubes/staff sem alterar o nome original. O teste
JavaScript real verifica tabelas de jogadores/staff/clubes, cabeçalhos de perfil,
tooltips e ausência de nome curto. Não foi repetida a suíte Chromium completa.

A instalação atualizada carregou o COR. Busca por Corinthians no staff exibiu
Corinthians na célula Clube, com Sport Club Corinthians Paulista no tooltip;
a mesma busca na aba Clubes mostrou Corinthians na coluna Nome. As referências
continuam vinculadas ao UID do clube. Fontes/bundle/ZIP e assinatura local
conferidos após a atualização.


## Seleção única e lista em grupo — 30/10/2026

Jogadores/staff passam a ter uma caixa por linha, com cabeçalho Selecionar.
A barra próxima à tabela oferece Comparar (exatamente dois), Adicionar à lista,
Limpar seleção e Remover da lista quando a lista/filtro de salvos está aberto.
A marca Na lista informa associação sem outro controle de seleção. A seleção
permanece entre pesquisas do mesmo tipo e é limpa ao trocar tipo/recarregar save.
Selecionar por teclado preserva o foco; durante a gravação, os controles ficam
desabilitados. Perfil pode selecionar/desmarcar e alterar a lista individualmente.

O endpoint em grupo valida carreira, tipo, IDs inteiros existentes e ação antes
de escrever. Adição/remoção são explícitas e idempotentes, com transação única,
sem apagar registros ao repetir Adicionar. A lista pessoal fica separada do save.
112 testes Python passaram, incluindo idempotência, lote inválido sem escrita,
rollback de falha real no SQLite e isolamento entre carreira/tipo.

35 fluxos Chromium passaram sem erros de console, com leitura/releitura do COR,
comparação, exportação/importação, listas, staff, clubes e quatro larguras de tela.
O fluxo novo cobre três selecionados para adicionar, dois para comparar, teclado
sem perder foco, repetição sem remover, rejeição de lote inválido e remoção em grupo.
A primeira execução parou em uma espera antiga de salários: a nacionalidade
esperada também existia no perfil anterior. O teste passou a aguardar o nome exato
do perfil antes de calibrar; a segunda execução terminou. Logs preservados em
`/tmp/fm-scout-ui-20261030-unified-selection-01.log` e `-02.log`.
Todos os testes de lista usaram armazenamento temporário isolado.

A instalação AppKit/WebKit carregou o COR e mostrou uma caixa por linha no Meu
time. Memphis e Gabriel Paulista foram marcados; o contador mostrou 2 selecionados
e os botões Comparar/Adicionar à lista ficaram habilitados usando essa seleção.
Não foi acionada escrita na lista pessoal durante a conferência nativa; ela foi
comparada com o snapshot anterior. Recursos do bundle/ZIP e assinatura conferidos.


## Selecionar todos no cabeçalho — 30/10/2026

A caixa no cabeçalho marca/desmarca as linhas carregadas da pesquisa atual,
reutilizando a seleção única e Adicionar à lista. Ela indica seleção parcial,
fica desabilitada com tabela vazia/carregamento/gravação e não altera seleções
que estejam fora das linhas carregadas. Carregar mais recalcula o estado;
novos resultados podem ser incluídos marcando o cabeçalho novamente.

O teste JavaScript real cobre total/parcial/vazio, desmarcar o lote preservando
uma seleção externa, novas linhas e bloqueio durante gravação. Os 112 testes
Python passaram. O teste Chromium completo foi atualizado para o cabeçalho,
mas não foi repetido nesta alteração pequena; a gravação em grupo foi validada
na execução anterior de 35 fluxos em armazenamento temporário isolado.

Na instalação AppKit/WebKit atualizada, o cabeçalho marcou os 68 jogadores do
Corinthians e habilitou Adicionar à lista. Desmarcar Memphis reduziu o contador
para 67; marcar e desmarcar pelo cabeçalho voltou de 68 a zero. Nenhuma adição
foi executada na lista pessoal; seu conteúdo permaneceu igual ao snapshot.
Fonte, recurso instalado e ZIP são idênticos; assinatura local conferida.

## Redesenho aprovado, EU e copiar nome — 30/10/2026

As referências foram implementadas no frontend de produção. Mapeamento, decisões,
limites visuais, arquivos e evidências em docs/REDESIGN.md; tokens/razões em DESIGN.md.
A suíte atual é qa/check_redesign.cjs, com dados COR reais e armazenamento isolado.
Passou 18 fluxos, sem erros de JavaScript/console; incluiu Clipboard API nas três
entidades, check temporário de 1,5s, filtros com rascunho/aplicar/cancelar, tabelas,
painéis, listas, presets, importação/exportação e quatro larguras. A comparação
visual usa o código/especificação do protótipo, cujo arquivo local foi bloqueado
pela política do navegador; não se declara paridade pixel a pixel.

112 testes Python e o JavaScript real passaram novamente. A ponte nativa nova
restringe cópia ao frame principal e porta local atual, string não vazia e até
1024 bytes. Swift compilado e assinatura local verificada.

Na instalação AppKit/WebKit, após o proprietário aprovar o acesso a Documentos,
o COR abriu: 63.514 jogadores, Meu time com 68 e coluna EU. Abrir Memphis mostrou
o perfil com o botão de copiar; o clique mudou o nome acessível para Nome copiado,
voltou a Copiar nome, e colar na busca produziu exatamente Memphis Depay, com
um resultado. A busca foi limpa e o elenco voltou a 68. Não houve adição/remoção
na lista pessoal durante essa conferência. O último ajuste de CSS remove a largura
excedente da faixa de abas do inspector, mantendo o painel com 340px.

A inicialização branca não foi atribuída ao layout: o processo Python aguardava
acesso ao ambiente do projeto em Documentos. O proprietário mostrou o aviso de
permissão e aprovou; nenhuma permissão geral do sistema foi alterada pelo agente.
Logs de tentativas e amostra de processo foram preservados em /tmp.

Em 31/10/2026, antes da publicação do redesign na PR #7, passaram novamente os
112 testes Python, check_money_fields.cjs, sintaxe JavaScript, typecheck Swift,
assinatura local e os 18 fluxos de check_redesign.cjs com zero erros de console/JS.
Log desta repetição: /tmp/fm-redesign-qa-pr-20261031.log. A execução usou
armazenamento temporário e preservou o piso de 20 GiB livres.
