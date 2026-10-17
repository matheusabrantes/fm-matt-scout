# Dívidas e empréstimos de clubes no save

Investigação em 17/10/2026. Fontes públicas primárias e bytes de uma cópia temporária do save COR; sem abrir o FM, acessar seu processo, alterar saves ou instalar dependências.

## O leitor público ainda não fornece dívida

A [API primária do PyPI](https://pypi.org/pypi/fmsave/json) ainda indica `0.5.10`, publicada em 11/10/2026. O [README do fmsave no commit f732460719d80d74287a48b15abd22607952bee2](https://github.com/rhiever/fmsave/blob/f732460719d80d74287a48b15abd22607952bee2/README.md#what-it-cannot-read) inclui dívida de clubes entre os campos não suportados. O [modelo FinanceMonth desse commit](https://github.com/rhiever/fmsave/blob/f732460719d80d74287a48b15abd22607952bee2/src/fmsave/models/finances.py) contém saldos e orçamento, mas não empréstimos, juros ou dívida líquida. Saldo negativo e fluxo mensal de transferências não são substitutos desses campos.

O [Gilet, commit 716bfc80fdabc6ab88be4e4908d9738ffc346b69](https://github.com/fifteen15-labs/gilet/tree/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src), continua sem leitor de dívidas ou finanças; seu [club.rs](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/club.rs) trata identificação e vínculos de clubes, não empréstimos.

## Evidência nova no arquivo

O COR examinado é `26.3.2+2329565`, data 29/12/2025. A cadeia mensal de finanças de Corinthians, UID público 318, tem último saldo de novembro de 2025 igual a `-4.905.676` unidades internas. Esse valor histórico não certifica o caixa atual nem permite calcular a dívida líquida do screenshot.

O contêiner inclui a seção `starting_club_debt_db`, de **2.753.172 bytes**. Há uma população regular de **34.849 registros completos de 79 bytes** a partir do offset 80, seguida de um último cabeçalho curto. Todos os registros completos satisfizeram índice sequencial e UID duplicado iguais; o início da seção declara 34.850 objetos. Esse teste estrutural identifica objetos, mas não atribui significados financeiros a todos os campos.

Nessa seção há exatamente **três** ocorrências da data 31/12/2060, nos offsets 2.519.742, 2.590.921 e 2.647.959. As três são precedidas pela data 01/01/2024 e possuem payload idêntico:

| Posição relativa à data final | Bytes lidos | Significado demonstrado |
| --- | --- | --- |
| −36 / −32 / −28 | Índice e duas cópias do UID | Cabeçalho de objeto |
| −23, inteiro u32 | 256 | ID da equipe principal do Corinthians, resolvido pelo índice de equipes do próprio save |
| −19, inteiro u32 | 106.192.712 | Candidato a valor original; cerca de €122 milhões pela escala monetária aproximada observada nesta carreira |
| −15, inteiro u32 | 432 | Não identificado |
| −9, inteiro u32 | 5 | Não identificado nesta seção |
| −4, data FM | 01/01/2024 | Data inicial |
| 0, data FM | 31/12/2060 | Data final |
| +4, float32 | 15,0 | Não identificado; não presumir taxa de juros |

Os pares índice/UID dos três objetos são `(31894,31896)`, `(32795,32797)` e `(33517,33520)`. O campo de equipe, em `objeto + 13`, resolve `256` para `(club_uid=318, slot=0)`, a equipe principal do Corinthians. Há quatro registros com essa equipe: um placeholder de valor zero e os três empréstimos descritos. A associação usa o índice de equipes do próprio arquivo; não depende de nomes ou de o usuário conhecer IDs. O contrato `team_to_club` é documentado pelo [ClubIndex do fmsave](https://github.com/rhiever/fmsave/blob/f732460719d80d74287a48b15abd22607952bee2/src/fmsave/readers/clubs.py): IDs de equipe são armazenados sem a correção `+1` aplicada ao UID público do clube. A seção se chama *starting*, portanto seus valores não se tornam saldo atual apenas porque o vínculo de clube foi resolvido.

No conjunto da seção, **3.270 registros têm valor não zero**. Destes, **2.899** resolvem o campo de equipe no índice, e **371** não: 165 têm o sentinela `0xFFFFFFFF` e 206 têm outro ID sem vínculo disponível. Os registros sem vínculo não podem ser descartados antes de verificar colisões. Há 3.063 fingerprints distintos `(valor original, bytes da data inicial, bytes da data final, código bruto)`; **2.634** têm todos os proprietários resolvidos a um único clube. Os demais permanecem ambíguos. O fingerprint do Corinthians possui somente equipe 256, clube 318.

A forma da tabela foi também conferida em uma cópia de Brasil, do mesmo build: mesmo comprimento, 34.850 objetos declarados, 34.849 registros completos e cabeçalho final curto de 21 bytes. Um helper experimental pode aceitar somente esse envelope (`80 + 79 × (contagem − 1) + 21`), exigir índice sequencial, UID duplicado e discriminador de objeto zero em todos os registros, e falhar sem resultados diante de truncamento ou divergência. O helper de proposta `/tmp/starting_loan_owners_proposal.py` retornou 2.634 fingerprints e rejeitou truncamento e corrupção de uma cópia do UID no self-check. Não foi copiado para o aplicativo por esta investigação.

A busca independente no `game_db` encontrou um grupo no `game_db` de **três registros consecutivos de 28 bytes**, com as mesmas datas e o mesmo candidato a valor original. Essa é uma trilha melhor para os valores atuais. O fingerprint corresponde unicamente ao Corinthians na tabela inicial, e a multiplicidade três coincide nas duas estruturas. Para generalizar, a leitura desse grupo deve validar a contagem/limites do grupo, preservar multiplicidade, rejeitar fingerprints de proprietários incompletos ou ambíguos e manter o vínculo experimental: um empréstimo novo de outro clube pode coincidir com termos antigos de um único clube. Uma referência estrutural de proprietário no objeto do `game_db` seria uma confirmação mais forte do que o fingerprint sozinho. Não reutilizar offsets de RAM nem escolher a ocorrência mais próxima de um nome.

No registro do `game_db`, o inteiro `526223` é candidato forte a prestação mensal: corresponde aproximadamente aos €608 mil mensais exibidos. Como controle numérico, uma anuidade de principal `106192712`, juros anuais de 5% divididos por 12 e 442 prestações resulta em `526223,819`; isso é compatível com o inteiro armazenado e o intervalo das datas. **Compatibilidade não certifica a fórmula usada pelo FM**, nem determina o valor restante ou os juros. Nenhuma fórmula inferida deve preencher a interface antes da confirmação dos outros campos.

## Referência do usuário e limites

A captura fornecida mostra dívida líquida de €759.877.074, dívida de transferências de −€3.857.086 e três empréstimos do tipo Município, com início em 01/01/2024 e fim em 31/12/2060. O jogo arredonda os valores das linhas; esses números servem como referência independente de conferência, nunca como constantes do programa. A referência é de Corinthians, mas a data corrente da tela não aparece na captura.

A ausência de dívida decodificada deve continuar como dado não lido, sem exibir zero, tomar orçamento como dívida, somar juros em duplicidade ou transformar automaticamente qualquer dívida de transferências negativa em zero. O significado do sinal e a composição de dívida líquida exigem conferência própria.

Auxiliares locais: `/tmp/fm-cor-club-debt.bin`, `/tmp/fm-starting-debt.bin` e `/tmp/fm-live-debt-context.json`. São recortes privados de investigação, não fazem parte do repositório nem devem ser publicados com o save.

## Resultado da investigação

O usuário confirmou que a imagem é da carreira COR já salva. A investigação não alterou o aplicativo nem adicionou totais inferidos. Dívida líquida, dívida de transferências, principal restante, juros e prestação mensal ainda não têm uma leitura completa validada. Os três contratos iniciais foram vinculados por equipe, mas o valor original não é dívida corrente e a correspondência de termos com outro bloco não substitui a decodificação do proprietário e dos saldos atuais. Não se implementou uma interface vazia ou com dados manuais da captura.

O SHA-256 do COR permaneceu `69c685db1ddd954386691909c987307440581f9b3621fb68825f7752fa8c89cc`, igual ao observado antes desta investigação. Somente documentação foi adicionada ao repositório; os protótipos e recortes binários ficaram em diretório temporário e não fazem parte da publicação.
