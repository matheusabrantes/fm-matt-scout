# FM Matt Scout

Direção aprovada em 30/10/2026: FM_MATT_SCOUT_DESIGN_SYSTEM.md e FM Matt Scout Prototype.dc.html. O app real é a fonte de regras/dados; o protótipo é a fonte visual. Mapeamento e diferenças em [docs/REDESIGN.md](docs/REDESIGN.md).

## Composição

Sidebar recolhível de 220px, toolbar de 52px, faixa de filtros de 46px, cabeçalho de 30px e linhas de 34px. Inspector de 340px fechado por padrão, aberto por seleção explícita e descartável. A tabela ocupa o espaço disponível para facilitar a leitura de grandes listas. Navegação: Jogadores, Staff, Clubes, Minha lista, Meu time e pesquisas salvas reais.

## Aparência e razões

- Branco e cinzas frios: superfícies neutras da referência para manter o foco nos dados.
- Azul #2F6FED: seleção e ações; cores de posição e familiaridade comunicam significados distintos.
- Tipografia de sistema: SF Pro no Mac, com números tabulares para comparação entre linhas.
- Densidade e espaçamentos da referência: mais registros legíveis por janela, sem cartões decorativos.
- Atributos na tabela: rampa contínua oklch(0.25 + 0.60t, 0.03 + 0.16t, 132), t=(valor−1)/19; no perfil, cor de texto por faixa. Números reais permanecem visíveis.
- Ícones SVG da referência: identificam navegação e controles; o ícone adicional de cópia foi pedido pelo usuário e muda temporariamente para check.
- Badges com as cores da base instalada do FM, associados pelo identificador do próprio registro do save. O fundo original é preservado; texto de contraste insuficiente usa branco ou preto para leitura. Paletas ausentes ficam neutras. As siglas existentes continuam identificando o clube; não são escudos oficiais.
- Alças nas bordas dos cabeçalhos: separar o ajuste de largura do clique de ordenação, com setas do teclado e foco visível. Divisórias em cinza claro #E5E5EA, com #C7C7CC no hover/arraste, suavizadas a pedido do proprietário; contorno azul apenas no foco pelo teclado. Larguras são salvas por tipo de tabela.
- Busca com largura padrão de 300px nas três listas: acomodar o placeholder completo e o atalho, mantendo ajustes responsivos em janelas estreitas.
- Sol/lua no extremo direito da toolbar: alternar imediatamente os temas claro/escuro, inclusive sem carreira aberta. Tokens da especificação fornecida em 31/10/2026; sem transição global de cores.
- Bandeiras locais com proporção fixa, cantos de 2px e contorno discreto: representar nacionalidades com a mesma geometria do protótipo, inclusive as quatro nações britânicas. A célula Nac reserva espaço para três bandeiras; perfis mostram todas as cidadanias lidas.
- Contratos em JUN 27: mês abreviado e ano curto facilitam a leitura; o tooltip mantém a data completa. As cores de proximidade continuam usando a data da carreira.

ENERGY 1 / RHYTHM 1 / MOTION 2. Transições de painéis .28s, sheets .22s e popovers .16s; respeitar redução de movimento. A densidade uniforme serve à comparação, e a animação mostra a origem de painéis/sheets.

## Estados e confiança

Sem save: arquivos reais e seletor nativo. Carregando: progresso real do leitor. Erros: mensagem legível. Campos não lidos: indisponíveis, nunca zero inventado. Ratings próprios conservam fórmulas/origem. Moeda depende de conversão conferida. Filtros em rascunho aplicam ou descartam com clareza. Nenhum dado ou cálculo simulado do protótipo entra na produção. Preservar acessibilidade, controles de teclado, persistência e todas as funções de produção ausentes da referência.
