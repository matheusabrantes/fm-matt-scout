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
