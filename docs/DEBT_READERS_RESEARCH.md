# Dívidas de clubes: leitores externos e significado dos campos

Verificado em 17/10/2026. Pesquisa somente em código público e arquivos locais do projeto. Não foi aberto o FM, acessada memória de processo, instalado plugin ou alterado save/dependência.

## Resultado

Nenhum dos leitores abertos examinados oferece um decoder de **dívida líquida, dívida de transferências ou empréstimos financeiros** do `.fm` do FM26. Isso não demonstra que os dados não existam no save. Demonstra que os leitores examinados ainda não fornecem a ponte entre o dado e seus bytes. Não há fórmula confirmada para reconstruir esses totais a partir do saldo e do histórico mensal.

### fmsave — formato de arquivo

O [guia de cobertura, commit f732460719d80d74287a48b15abd22607952bee2](https://github.com/rhiever/fmsave/blob/f732460719d80d74287a48b15abd22607952bee2/docs/guides/what-a-save-holds.md) explicita club debt entre os campos não expostos, ressalvando que isso não determina se o save os armazena.

O [modelo FinanceMonth](https://github.com/rhiever/fmsave/blob/f732460719d80d74287a48b15abd22607952bee2/src/fmsave/models/finances.py) oferece histórico mensal. Seus campos têm estes significados e limites:

| Campo | Significado documentado | Não confundir com |
| --- | --- | --- |
| `balance` | Caixa no final do mês; a primeira linha de algumas séries é abertura | Dívida líquida ou total de empréstimos |
| `net_transfers` | Fluxo de transferências do mês, positivo para gasto líquido; sem confirmação no jogo | Obrigações de parcelas futuras ou “Dívida de Transferências” |
| `net` | Receita menos despesa do mês | Patrimônio ou dívida líquida |
| `transfer_budget_remaining` | Verba de transferências disponível | Caixa ou montante a pagar a outros clubes |
| `total_expenditure` | Despesas do mês; sem confirmação no jogo | Saldo devedor remanescente |

O modelo avisa que dinheiro permanece na unidade interna do save. Converter para euros exige calibração da mesma carreira; salário semanal e prestação mensal têm períodos diferentes. Uma calibração aproximada obtida de `1,72M` não certifica euros unitários em um total como `759.877.074`.

### FM AI Assistent — RAM, sem dívidas no exportador

O [ClubExporter, commit 12ab90d1ae322103daa218737e20f8729cfc36ef](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/src/main/java/com/github/fmaiassistent/exporter/ClubExporter.java#L128) lê somente `balance`, `transferBudget` e `payrollBudget` para finanças. Além disso, arredonda os valores antes de exportá-los. Não há campos de dívida, empréstimos financeiros, juros ou parcelas em `FIELD_NAMES`, no record `Finance` ou nas buscas pelo restante do repositório.

O [ClubRecordLayout do mesmo commit](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/src/main/java/com/github/fmaiassistent/memory/ClubRecordLayout.java) descreve ponteiro `club + 0x150`, assinatura financeira `0xB318`/`0xD2E8` no exportador e três offsets relativos: caixa `0x14`, orçamento de transferências `0x7CC`, orçamento salarial `0x810`. São endereços de objetos vivos em RAM, **não offsets do arquivo serializado**. Não foram aplicados ao `.fm`.

### FMSuperScout — RAM e empréstimos de jogadores

O [Dumper, commit 759b9cc35f5e156b01c901b2fa24c37903fad1b0](https://github.com/mavarobli/FMSuperScout/blob/759b9cc35f5e156b01c901b2fa24c37903fad1b0/plugin/Dumper.cs#L1038) exporta pessoas, atributos, salário e valor de transferência. `LoanListed`/`OwnerClub` e os relatórios de `loans` representam jogadores emprestados. Não são contratos bancários. A busca no repositório não encontrou estrutura de dívida financeira. O [README desse commit](https://github.com/mavarobli/FMSuperScout/blob/759b9cc35f5e156b01c901b2fa24c37903fad1b0/README.md) descreve BepInEx e acesso ao processo; não foi executado.

### Gilet — formato de arquivo

O [formato documentado, commit 716bfc80fdabc6ab88be4e4908d9738ffc346b69](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/docs/SAVE_FORMAT.md) e `crates/fm-save/src` não possuem decoder ou campo de dívida bancária. Ocorrências de `loan` referem-se à relação entre jogador, clube do contrato e clube de inscrição.

### FMRTE — exibe os dados, sem schema público examinado

A [documentação oficial de finanças](https://docs.fmrte.com/clubs/finances/) confirma uma lista Debt and Loans com dívida original, pagamentos, juros e datas. Define Balance como caixa atual. Não publica offsets do save, fórmula de dívida líquida ou um schema de exportação dos contratos financeiros. Essa documentação prova a existência da informação no produto; não permite implementar um importador sem amostra real.

## Referência fornecida pelo usuário

O screenshot do Corinthians mostra dívida líquida `€759.877.074`, dívida de transferências `−€3.857.086` e três contratos municipais com início `01/01/2024`, vencimento `31/12/2060`, original aproximadamente `€122M` cada e remanescente aproximadamente `€118M` cada. A linha Global traz aproximadamente `€355M`, `€422M` entre parênteses e pagamento mensal `€1,82M`.

Esses valores abreviados não são números exatos. O screenshot não informa a data da carreira nem demonstra se o valor entre parênteses é juros isolados ou total com juros. Não somar automaticamente as duas colunas nem impor uma fórmula contábil genérica ao total do FM. A comparação válida requer o save e a tela na mesma data.

## Receita para repetir a busca e avançar

1. Obter os repositórios acima nos commits citados, sem executar os leitores externos. Buscar `debt`, `netDebt`, `transferDebt`, `repayment`, `instalment`, `installment` e `loan` com `rg -ni`. Inspecionar cada `loan`: maioria é empréstimo de jogador ou empréstimo interno de buffer.
2. No save descomprimido, usar contratos com **datas conhecidas** como âncoras estruturais. A repetição de três contratos iguais com início/vencimento conhecidos é mais informativa que procurar apenas um total convertido/arredondado. Proximidade de um cabeçalho de clube, sozinha, não comprova vínculo.
3. Aceitar um decoder somente quando contagem, datas, identidade do clube e múltiplos valores monetários conferirem; incluir clubes sem dívida e contratos de tipos diferentes. A estrutura precisa funcionar em outra carreira/build e rejeitar listas truncadas ou ambíguas.
4. Se surgir exportação real externa já existente, antes de criar importador registrar: produtor/build, carreira e data do snapshot, moeda/unidade, período das prestações, identificador estável do clube e significado de juros/total. Associar por chave interna comprovada, mantendo nomes na interface; dados ausentes são desconhecidos, não zero. Não foi localizado ou recebido arquivo real desse tipo nesta pesquisa.

Não foi criado parser especulativo nem preenchida dívida como saldo negativo. A investigação direta do arquivo deve ser documentada separadamente com os resultados e os limites encontrados.
