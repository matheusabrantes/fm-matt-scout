# Dívida atual dos clubes

## Estado em 29/10/2026

A dívida atual ainda não tem um decoder seguro para a interface. A [cobertura pública do fmsave](https://github.com/rhiever/fmsave#what-it-cannot-read), conferida nesta investigação, continua incluindo dívida de clubes entre os campos não suportados. O código instalado `fmsave==0.5.10` lê o histórico financeiro mensal, mas não entrega dívida líquida, transferências a pagar/receber ou empréstimos financeiros.

Saldo, verba de transferências e dívida são campos diferentes. Não preencher dívida com saldo negativo, somar somente os valores originais dos empréstimos ou apresentar ausência de leitura como zero.

## Fonte e preservação

Foi criada uma cópia temporária da carreira COR; tamanho e `mtime` do original foram comparados antes/depois da cópia. O arquivo examinado tem 74.749.036 bytes, build `26.3.2+2329565`, data da carreira **30/12/2025** e SHA-256 `7010e6db21345f51e2c1a4b00788e21994daae7ae998a271b9d75661f965e8a0`. Os recortes binários, o save e seus mapas de identidade ficaram somente em `/tmp`; não devem ser publicados.

A confirmação independente no FM aberto, na mesma data, foi feita nesta sessão:

| Corinthians | Valor exibido |
| --- | ---: |
| Dívida líquida / restante | € 759.886.500 |
| Dívida original | € 368.636.471 |
| Dívida de transferências | −€ 3.857.086 |
| Saldo global | € 14.441.698 |

A tela detalhada mostra três empréstimos Município iguais: início em 01/01/2024, vencimento em 31/12/2060, original abreviado de €122M cada, restantes de €118M e €140M entre parênteses, pagamento mensal de €608 mil. A linha global abrevia os restantes como €355M (€422M) e o pagamento mensal como €1,82M. As abreviações não fornecem números exatos para principal e juros separados.

Essas são referências de conferência, **não dados para preencher o aplicativo nem constantes do parser**. Também não demonstram por si só a fórmula de dívida líquida do FM.

## Estrutura inicial já identificada

A seção `starting_club_debt_db` tem 2.753.172 bytes e o mesmo envelope da análise anterior: cabeçalho de 80 bytes, 34.849 objetos completos de 79 bytes e um último cabeçalho curto de 21 bytes. Os objetos completos passam por índice sequencial, UID duplicado e discriminador zero.

O campo de equipe em objeto +13 resolve no `team_to_club` do próprio save. Os três empréstimos do Corinthians apontam à equipe 256, vinculada ao clube UID 318. Cada um armazena valor original `106192712`, o inteiro `432` em +21, tipo bruto `5` em +27 e datas 01/01/2024–31/12/2060. A existência de uma seção *starting* impede tratar seu principal original como dívida corrente.

## Avanço no bloco atual

O `game_db` desta cópia tem 170.052.961 bytes. Os três registros correspondentes aparecem em **55.713.867**, **55.713.895** e **55.713.923**, consecutivos e precedidos de uma contagem explícita igual a três. A linha tem 28 bytes:

| Offset relativo à linha | Tipo | Valor no Corinthians | Situação |
| --- | --- | ---: | --- |
| +0 | byte | 1 | Não identificado |
| +1 | u32 | 106192712 | Coincide com o principal original, não com principal restante confirmado |
| +5 | u32 | 526223 | Candidato forte a pagamento mensal |
| +9 | u32 | 285968 | Não identificado |
| +13 | u32 | 0 | Não identificado |
| +17 | data FM | 31/12/2060 | Conferida na tela |
| +21 | byte | 5 | Coincide com o código inicial; a tela deste caso diz Município |
| +22 | u16 | 1 | Não identificado |
| +24 | data FM | 01/01/2024 | Conferida na tela |

Uma busca limitada às assinaturas de datas/tipo e ao fingerprint completo `(valor original, início, fim, tipo)` encontrou **131 linhas** com correspondência em contratos iniciais. Dessas, **108 linhas** formam **74 listas** cuja contagem armazenada coincide com o número de linhas consecutivas reconhecidas. Todos esses 74 fingerprints apontam para um único clube na tabela inicial.

Isso estende a análise anterior de um clube para dezenas de listas. Ainda é uma correspondência entre termos: um empréstimo novo de outro clube pode ter exatamente os mesmos termos. Uma lista contendo empréstimo sem fingerprint inicial também pode ficar parcialmente reconhecida. O parser de produção precisa de uma referência estrutural de proprietário e um envelope completo antes de generalizar. A busca foi limitada e não demonstra que só existam 131 empréstimos atuais no save.

## Conferência monetária e fórmula ainda não validada

Os três principais originais somam `318578136` unidades internas. O total original exato mostrado pelo FM implica aproximadamente **1,157130478659 EUR por unidade interna** nessa data. Essa escala também converte o saldo `12480613` encontrado no registro próprio do Corinthians em aproximadamente €14.441.698, oferecendo uma segunda conferência independente. Isso não é uma cotação global para outros saves ou datas.

Usando essa escala e os totais da tela, a expressão exploratória

`(dívida líquida + saldo − dívida de transferências) / (3 × 526223 × escala)`

resulta em `426,000000738`. A equivalência numérica com **426 prestações** é forte. Mas da data atual 30/12/2025 até 31/12/2060 há aproximadamente **420 meses**, não 426. Portanto não se pode inferir o contador a partir dessas datas nem assumir que o inteiro inicial 432 menos os meses transcorridos sempre reproduza o comportamento do jogo.

O alvo de dívida líquida, aproximadamente `656699062` unidades internas, não aparece como inteiro de 32 bits (busca ±2) no `game_db`, nem o total exploratório `672512994` de 426 prestações. Isso sugere um total calculado, sem provar a fórmula. O significado do campo `285968`, a identidade estrutural da lista e o saldo devedor/juros individuais continuam sem confirmação.

## Segunda etapa: outra carreira e decomposição das parcelas

Uma cópia temporária de Brasil, de 29/12/2025 no mesmo build, tem SHA-256 `55ff168791edf6d3d1e0eb9e51b0557af457150d5e40a5c4ebb146601e1ce130`. Os três empréstimos aparecem em offsets diferentes, mas seus 28 bytes são **idênticos** aos do COR em 30/12/2025. Isso confirma a forma repetida em outra carreira; não valida o contador ou a dívida corrente. O arquivo original também foi conferido por hash ao final.

Há uma nova decomposição aritmética consistente em três empréstimos distintos:

| Caso | Original | Parcela +5 | Campo +9 | Original ÷ (parcela − campo +9) |
| --- | ---: | ---: | ---: | ---: |
| Corinthians, cada linha | 106192712 | 526223 | 285968 | 442,000008 |
| Burnley, primeira linha | 92200000 | 1329708 | 205318 | 82,000018 |
| Burnley, segunda linha | 20200000 | 171186 | 0 | 118,000304 |

Os quocientes são praticamente inteiros, com a diferença esperada do arredondamento da parcela para inteiro. São também dois meses menores que os intervalos de calendário completos das respectivas datas originais. Isso torna `campo +9` um candidato forte a **juros mensais fixos**, e `parcela − campo +9` a amortização mensal do principal. Ainda é uma inferência, não um rótulo confirmado no formato.

No Corinthians, multiplicar os dois componentes por 426 parcelas e pela escala observada resulta em principal restante global de aproximadamente **€355.292.157,67** e juros restantes de **€422.893.124,99**, coerentes com as abreviações independentes €355M (€422M) mostradas pelo FM. A correspondência reforça os componentes, mas não resolve de onde vêm as 426 parcelas restantes. Nenhum inteiro de 16 ou 32 bits igual a 426 ou 432 está nos 1.500 bytes anteriores/1.000 posteriores ao grupo; não colocar um contador arbitrário na implementação.

A região descomprimida não listada `unlisted_after_non_pl_hist_ls`, de 51.877.697 bytes, foi examinada em streaming por assinaturas específicas: principal original, os dois campos monetários da parcela do Corinthians, o alvo de dívida líquida e o total exploratório de prestações. Nenhuma dessas assinaturas apareceu. A busca não identifica o significado dos demais bytes nem exclui um estado de empréstimos representado de outra forma.

## Critérios para implementar

1. Localizar a referência estrutural do proprietário de cada lista atual, resolvida pelo índice do próprio save, sem proximidade de nomes/IDs ou associação só por termos.
2. Interpretar o contador e os valores atuais com controles independentes de mais de um clube, incluindo empréstimos de outro tipo e clube sem dívida.
3. Validar composição e sinal da dívida de transferências, saldo e juros; conservar separadamente as grandezas observadas e derivadas.
4. Exigir envelope, contagem e limites completos; rejeitar registros truncados, versões não verificadas e proprietários ambíguos.
5. Usar a moeda/escala da carreira. A calibração salarial abreviada anterior não certifica totais em euros unitários.

Nenhum parser, coluna com valores inferidos ou constante extraída da tela foi adicionado por esta análise.

## 30/10/2026: proprietário estrutural e leitura dos termos atuais

Nova cópia COR, já salva em 30/12/2025 às 15h, SHA-256
`3795481a7bebcdd4512f3c1419b3c0890adda042dc1f5fa74cb73b92874cde8d`.
Seu `game_db` descomprimido tem **170.268.292 bytes**. Os offsets abaixo pertencem
a essa cópia, não são constantes do leitor.

Foi localizada uma tabela paralela de objetos de clube em **55.573.460**:
contagem u32 **37.346**, seguida do primeiro cabeçalho em **55.573.464**.
Os cabeçalhos armazenam ordinais u32 consecutivos de zero a 37.345; o último
começa em **73.556.136**. A posição inicial é encontrada no arquivo por assinatura
e validação de todos os cabeçalhos, sem offset, nome ou valor monetário fixo.

O ordinal corresponde a **índice bruto do clube + 1**, obtido do registro básico
cujo UID duplicado coincide com `ClubRecordSpan.club_uid`. Isso equivale às chaves
de `ClubIndex.uid_by_club_index` do fmsave. Controles independentes:

| Clube | Índice bruto | Ordinal da tabela atual | Início do objeto atual | Início da primeira linha de empréstimo |
| --- | ---: | ---: | ---: | ---: |
| Boca Juniors, UID 82 | 15 | 16 | 55.587.329 | 55.587.918 |
| Corinthians, UID 318 | 163 | 164 | 55.713.224 | 55.713.867 |
| Burnley, UID 622 | 347 | 348 | 55.906.619 | 55.907.622 |
| Real Madrid, UID 1734 | 1137 | 1138 | 56.711.993 | 56.712.792 |

**Todas as 74 listas anteriormente reconhecidas apenas pelos termos ficaram
dentro do objeto do proprietário esperado.** A associação do novo leitor usa
o ordinal e o UID do registro básico, e não esses fingerprints. A ordem de clubes
aceitos em uma lista Python não pode substituir o índice bruto: há slots ausentes.

O cabeçalho possui uma lista variável de referências: sua contagem está em +7,
as entradas ocupam quatro bytes e o primeiro conjunto de seis datas começa em
`19 + 4 * contagem`. Há um byte igual a um, seguido de outro conjunto de seis
datas. Os dois primeiros bytes depois do ordinal têm intervalo observado 0–20;
não se atribuiu significado a eles neste leitor. Essa estrutura resolveu vinte
falsos candidatos inicialmente encontrados em atributos/uniformes do objeto
anterior. A busca final encontrou **um único candidato por ordinal**, com tamanho
máximo observado de objeto de 6.164 bytes. O leitor limita a distância de busca
a 12.000 bytes e rejeita toda a tabela se faltar um ordinal ou houver ambiguidade.

Dentro do objeto delimitado pelo próximo cabeçalho, a lista atual tem contagem
u32, linhas de 28 bytes e um bloco posterior com contagem u16 de itens de 11 bytes.
No formato verificado, cada item posterior começa com o código dois. Em seguida
há um campo de quatro bytes compatível com data de fundação, uma referência
`FFFFFFFF`, um u16, texto UTF-8 com comprimento u32, contagem byte e objetos de
uniforme de 27 bytes. Esses elementos e seus limites validam o envelope; o leitor
não publica significado dos campos ainda não confirmados. Datas de fundação
desconhecidas com ano zero e textos com acentos também existem.

Os bytes +22 e +23 da linha são dois campos, com +23 podendo ser um. Não se deve
exigir o u16 inteiro igual a um. Um empréstimo do Espanyol, UID 1708, armazena
`-1` no campo de juros mensais: o leitor conserva os outros termos e retorna
juros indisponíveis (`None`), sem convertê-los em zero.

Foi acrescentado **`club_debt.py`**, função
`read_current_club_debts(game_db, spans, build)`, restrita ao build verificado
`26.3.2+2329565`. Os valores permanecem na moeda interna e são identificados
como **valor original**, pagamento mensal e juros mensais, acompanhados de datas,
tipo e flags brutos. O resultado distingue uma lista vazia validada de um clube
sem leitura. O último objeto da tabela não é lido porque seu limite final não
foi verificado.

Verificação na cópia acima: **33.765 de 33.884 proprietários aceitos** tiveram
lista única validada: **139 listas não vazias** e **33.626 vazias**. Outros 119
objetos tinham envelopes vazios ambíguos e foram omitidos. Não representam uma
afirmação de dívida zero. As 74 listas dos controles anteriores passaram com
quantidades e proprietários exatos. A leitura por mmap levou 13,07 segundos;
a otimização de busca foi comparada com os 33.765 resultados anteriores completos,
sem diferença. Sete testes sintéticos cobrem propriedade, termos iguais em clubes
vizinhos, listas variáveis, limites, duplicidade, build, juros ausentes e ambiguidade.

Na conferência independente do Real Madrid no editor aberto do FM, o primeiro
empréstimo mostra original **€995.000.022**, mensalidade **€3.829.258**, juros
mensais **€1.460.211**, início 01/03/2020 e fim 30/03/2055. A linha atual lida
contém `859885760`, `3309271`, `1261924` e as mesmas datas. O segundo original
mostrado é **€340.000.001**, correspondente ao valor interno `293830304`.
Isso confirma o significado de +9 como juros mensais, anteriormente só inferido.

**O contador restante e a dívida líquida atual continuam em aberto.** Os inteiros
426 e 432 no fim do objeto próprio do Corinthians pertencem a sequências repetidas
de outras estruturas, não validam um contador de parcelas. O novo leitor não
produz total de dívida corrente, não usa a data final para estimar saldo e não
converte principal original em dívida atual. As seções anteriores descrevem a
evolução da investigação; esta seção substitui a pendência de proprietário e a
hipótese sobre +9, mas conserva a pendência de saldo atual.
