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
