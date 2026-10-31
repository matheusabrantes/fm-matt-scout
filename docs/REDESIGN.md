# Implementação do desenho aprovado

Referências fornecidas em 30/10/2026: FM_MATT_SCOUT_DESIGN_SYSTEM.md e FM Matt Scout Prototype.dc.html, lidos em conjunto. A produção continua sendo a fonte de regras e dados. Linguagem visual Atelier com cores de atributos Console. Energia 1, ritmo 1, movimento 2.

## Mapeamento

| Produção | Desenho aplicado | Preservação |
| --- | --- | --- |
| AppKit + WKWebView + HTTP local autenticado | Shell da referência e toolbar 52px | Mesmo processo/leitor, seletor e exportação nativos; chrome de janela gerenciado pelo macOS |
| Navegação por data-view | Sidebar 220px, grupos Banco de dados/Scouting/Pesquisas salvas | Jogadores, staff, clubes, lista e meu time |
| Busca e oportunidades | Busca na toolbar, segmentos e tokens | Mesmo endpoint, datas e critérios |
| Pesquisa avançada | Sheet 860px, abas e campo claro | Intervalos inclusivos, ocultos, goleiros, movimentos, reputações e multisseletores |
| Estado dos filtros nos controles | Snapshot enquanto sheet aberta | Contagem real; Aplicar confirma, Esc/scrim descarta |
| Colunas e layouts no disco | Popover 540px, grupos e presets de atributos | Seleção persistida por tipo e ordenação lógica; layout existente não é substituído |
| Tabela de entidades | Cabeçalho 30px, linhas 34px, zebra, seleção azul | Ordenação, numeração, carregar mais, seleção de todos, comparação e ações em lote |
| Atributos visíveis | Heat cells 30×22, oklch contínuo | Valores reais, mesma ordenação e soma |
| Perfil sempre presente | Inspector 340px, fechado por padrão | Abre por nome/linha/setas, fecha por botão/Esc/mesma linha |
| Familiaridade e ratings | Campo, três faixas e lista ordenada | Familiaridade real 1–20; avaliações próprias em divulgação progressiva |
| Relatório, evolução, estilo e empréstimos | Mais informações no inspector | Conteúdo e origem continuam acessíveis |
| Moeda/salário e calibração | Menu no cartão de save + sheet de conferência | Conversão verificada, persistência por carreira/moeda e precisão dos filtros |
| Lista pessoal | HUD e estrela no perfil | Ações idempotentes, importar/exportar reais; Desfazer usa somente IDs efetivamente alterados |

## Decisões e diferenças documentadas

- Tokens, ícones, espaçamentos e transições vêm das referências, para reproduzir a direção aprovada; não foi adotada biblioteca visual nem framework.
- Tabela semântica HTML mantida para preservar acessibilidade, colunas e ordenação. CA/PA compartilham apresentação quando ambos estão visíveis, com dois botões de ordenação independentes. Os dois campos continuam independentes no layout salvo.
- A numeração e a caixa única de seleção no cabeçalho/linhas continuam, inclusive para staff: são requisitos existentes que o protótipo não representa.
- Layouts já salvos prevalecem. Os padrões do novo desenho se aplicam a quem ainda não tem layout; o botão Restaurar padrão usa os padrões atualizados.
- Sidebar/inspector usam as medidas aprovadas no Mac; em telas abaixo de 700px a navegação e o inspector podem sobrepor o conteúdo para manter a interface utilizável. A toolbar reduz a busca e mantém título truncado, sem reproduzir a colisão conhecida do protótipo.
- Foco visível, controles semânticos, nomes acessíveis, inert no inspector fechado e redução de movimento preservados. Rótulos auxiliares usam o cinza de texto secundário legível. A rampa de heat cells é exatamente a aprovada, inclusive a troca de texto em 12; não implica uma certificação global de contraste AA.
- Bandeiras usam os glifos locais do sistema para países reconhecidos por Intl.DisplayNames, sem chamadas a CDN. País não reconhecido permanece por nome, sem inventar bandeira. Badges neutros são abreviações do nome real, sem inventar escudos/cores oficiais ausentes no leitor.
- Nenhuma taxa de câmbio, valor, posição, atributo, contagem ou loading simulado foi copiado do protótipo. As barras de capacidade/familiaridade usam as escalas reais 200/20.
- As abas adicionais de produção ficam em Mais informações. Staff mantém acesso a personalidade/estilo/contrato e todos os campos decodificados, incluindo legado identificado.
- A política do navegador impediu abrir o arquivo local do protótipo. A comparação usa o código HTML e a especificação fornecidos; não houve contorno da restrição. As capturas da aplicação real são usadas para conferir geometria, estados, cores e navegação.
- A implementação foi concluída localmente; a publicação na PR foi solicitada pelo proprietário em 31/10/2026. Merge permanece pendente de revisão.

## Validação

Resultados e diferenças estão registrados abaixo; a conferência nativa complementa os testes em Chromium.

### Resultados automatizados

- 112 testes Python passaram, incluindo leitores, contratos, moedas, filtros, layouts, médias e atomicidade das listas.
- qa/check_money_fields.cjs passou com JavaScript real: ordenação de colunas, valores exatos/compactos, fatores por período/moeda, nomes curtos, seleção, ausência de nome de clube, familiaridade 0/1/10/11/17/18/20, cor oklch exata em 20, título EU e cópia do nome nas três entidades pela ponte nativa simulada.
- qa/check_redesign.cjs passou em 18 fluxos integrados com o COR real, armazenamento temporário, zero erros de console/JavaScript. A execução 08 também leu a área de transferência depois de clicar em copiar jogador/staff/clube, conferiu o nome exato, o estado Nome copiado e sua volta após 1,5 segundo.
- Geometria medida em 1440px: sidebar 220, toolbar 52, filtros 46, cabeçalho 30 e linhas 34. Inspector abre com 340 e fecha com zero. Janelas 1280/1024/850/390 sem overflow global nem sobreposição de título/ações.
- Cobertura: tela inicial, loading real, navegação, atalhos, 100→200 linhas, numeração, cabeçalho total/parcial, comparação, lote idempotente e Desfazer, perfis/abas, posições reais, draft/aplicar/cancelar filtros, multisseletores, mínimos de atributos, presets, colunas/cores/layouts, staff, clubes/finanças/empréstimos/elenco, importar/exportar JSON e moeda/período.
- Logs de execução preservados em /tmp/fm-redesign-qa-01.log até -08.log; capturas em /tmp/fm-matt-redesign-20261030. As primeiras passagens registram a correção do nome de clube nulo, cancelamento de perfil com resposta atrasada e filtros que vazavam entre seções. Nenhum número de sucesso dessas passagens interrompidas foi contado como suíte concluída.
- A suíte atual de apresentação é qa/check_redesign.cjs. qa/check_ui.cjs conserva o roteiro anterior à troca de navegação e não foi repetida/adaptada integralmente nesta etapa; verificações monetárias e de dados permanecem nas suítes Python/JavaScript, e os fluxos atuais ficam na suíte nova.

### Complementos pedidos durante a implementação

- Cabeçalho EU, mantendo regras e filtro de todas as cidadanias.
- Ícone de copiar junto ao nome nas três entidades. No Mac usa NSPasteboard via mensagem do frame principal/mesma porta local; no navegador usa Clipboard API. Nome curto dos clubes acompanha o título exibido. Não copia IDs nem HTML.
- Feedback somente no próprio ícone: check por 1,5 segundo, título/nome acessível Copiado, sem diálogo ou toast de sucesso. Falhas da Clipboard API continuam visíveis como erro.

### Adaptações de produção

- A janela usa conteúdo em toda a área, título oculto e barra transparente. Uma NSToolbar unificada em modo iconOnly integra os controles reais do macOS à toolbar web de 52px, sem uma faixa de título adicional.
- O título e as áreas junto aos controles nativos deixam os eventos chegar ao AppKit; busca, filtros, tema e botão da sidebar continuam no WebKit. A região do título acompanha a geometria real por ResizeObserver, com ponte restrita ao frame principal e à mesma porta local. Arraste e duplo clique permanecem sob responsabilidade do macOS.
- Meu time mantém a ordenação contínua e o ranking/numeração solicitados anteriormente, em vez de reordenar os resultados em grupos de posição. O filtro de equipe continua no sheet.
- Colunas são confirmadas por Salvar layout, preservando o fluxo de persistência real, em vez do localStorage imediato do protótipo. Layout existente não é substituído pelo padrão novo.
- Informações de identificação/leitura do jogador ficam numa expansão dentro de Atributos; os atributos aparecem primeiro. Relatório, evolução, estilo e empréstimos continuam em Mais informações.
- A instalação depende da .venv do projeto em Documentos. O macOS solicitou acesso à pasta após reconstrução; o proprietário identificou o aviso e aprovou. Não foi alterada nenhuma permissão geral do sistema.

### Gate visual e de interação

- Hard Gate PASS no escopo funcional: dados reais, ações conectadas, estados vazio/loading/erro, controles semânticos, nomes acessíveis, foco e Esc; testes de resize e nenhuma rede externa de assets. A rampa de cores aprovada tem a limitação de contraste descrita na referência, preservada por instrução explícita; não se declara conformidade AA global.
- Purpose Gate PASS: motivos de cor, tipografia, ícones, densidade, espaçamento e animações estão em DESIGN.md e no mapeamento acima. Sem elementos decorativos ou números de demonstração.
- Liveliness PASS: energia 1/ritmo 1/movimento 2; a tabela é o foco, azul sinaliza seleção e as transições indicam abertura/origem dos painéis.
- Craftsmanship PASS no escopo conferido: 18 fluxos reais, testes de dados, cópia nas três entidades, quatro larguras e estados principais capturados. Comparação do protótipo por fonte/especificação; sem alegação de equivalência pixel a pixel ou auditoria de contraste completa.

### Conferência nativa e arquivos finais

No AppKit/WebKit instalado, COR abriu com 63.514 jogadores e Meu time com 68.
O cabeçalho EU foi conferido. Copiar Memphis Depay mostrou o check (nome
acessível Nome copiado), voltou ao ícone original e colou exatamente Memphis
Depay na busca. Limpar a busca recuperou os 68 jogadores.
A execução 09 da suíte integrada repetiu os 18 fluxos com zero erros, incluindo
cópia nas três entidades e ausência de overflow horizontal do inspector.

Os hashes de todos os JSON pessoais (layouts, filtros e calibrações) e os três
registros da shortlist permaneceram idênticos ao snapshot anterior. Recursos
web e módulos alterados do workspace, bundle instalado e ZIP foram comparados
byte a byte. Assinatura local verificada. O piso de 20 GiB foi respeitado.

Arquivos alterados:

- web/index.html: shell, sidebar, toolbar, sheets, estados e containers reais.
- web/style.css: tokens, layout, tabelas, inspector, responsividade e estados.
- web/app.js: apresentação, navegação, rascunhos, posições, formatação compacta,
  cópia e conexões aos endpoints existentes.
- macos/App.swift: mensagem restrita copyName para NSPasteboard.
- server.py: disponibiliza nacionalidades/situação contratual para a tabela e
  autoriza a coluna contratual existente; não altera o leitor.
- scout.py: autoriza ordenação pela data contratual já lida.
- qa/check_redesign.cjs: roteiro integrado da interface atual.
- qa/check_money_fields.cjs: conserva checks monetários e cobre novas funções.
- DESIGN.md, README.md, docs/QA.md e este relatório: direção atual e evidências.

Instalação: /Applications/FM Matt Scout.app. Pacote: dist/FM Matt Scout.zip.
A publicação do redesign na PR #7 foi solicitada pelo proprietário em 31/10/2026,
após a instalação local. Os 112 testes Python, as verificações JavaScript,
o typecheck Swift, a assinatura local e os 18 fluxos integrados passaram novamente
antes do commit. Log: /tmp/fm-redesign-qa-pr-20261031.log. Merge permanece pendente.
A assinatura local pode provocar nova solicitação de Documentos após atualizações;
o diálogo é gerenciado pelo macOS e a aprovação é feita pelo proprietário.

A PR #7 foi mesclada antes do push do redesign. Por isso, estas mudanças seguem
em uma PR complementar para main, sem repetir as alterações já mescladas.

### Integração da janela — 31/10/2026

- `python3 qa/check_native_window.py`: 376 verificações aprovadas sobre as classes reais do app, com servidor de fixture local e arquivos temporários isolados. Cobre 40 combinações de tamanho/sidebar/ações, mínimo de 850×600, controles nativos centrados na faixa de 52px, hit testing e validação da ponte. Entrada/saída de tela cheia e minimizar/restaurar foram confirmados por notificações e estado do AppKit.
- A compilação otimizada foi conferida com dados reais: busca e títulos Jogadores/Staff/Clubes, temas claro/escuro e 10 ciclos de recolher/expandir a sidebar. Cliques no botão da sidebar e no tema passaram pela toolbar. Duplo clique com sidebar aberta e recolhida ampliou e restaurou a janela.
- A automação em segundo plano não desloca nem a janela original. O proprietário confirmou com mouse real, na compilação final isolada, que arraste pelo cabeçalho e redimensionamento pela borda funcionam.
- A alteração funcional fica em `macos/App.swift`; HTML, CSS, componentes, leitores e dados pessoais não foram alterados. A compilação de QA usa armazenamento separado. Não houve atualização do bundle instalado nem do ZIP nesta etapa.
