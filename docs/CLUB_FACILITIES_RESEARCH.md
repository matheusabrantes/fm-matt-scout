# Instalações de treino e formação: investigação do formato

Verificado em 13/10/2026. Escopo: código público, arquivos estáticos da instalação e uma cópia temporária de COR. Não foi aberto o FM, lida a memória do processo ou alterado o save, a instalação ou as dependências.

## Resultado prático

Foi encontrada uma fonte primária que lê **quatro medidas diferentes** de instalações no FM26: treino, formação, treinamento de jovens e recrutamento de jovens. Entretanto, ela descreve objetos **na RAM**, não o formato serializado do `.fm`. Ainda não há um vínculo demonstrado entre esses quatro campos e bytes de COR. Não é seguro preencher colunas atuais com esse material.

A ausência dessas medidas no `fmsave` não significa que não existam no jogo ou no save. A nova trilha indica que procurar somente junto às instalações corporativas é insuficiente: elas pertencem a outro bloco na fonte adicional.

## Fonte adicional: objeto de instalações separado das finanças

O [ClubRecordLayout do FM AI Assistent, commit 12ab90d1ae322103daa218737e20f8729cfc36ef](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/src/main/java/com/github/fmaiassistent/memory/ClubRecordLayout.java) e o [leitor ClubExporter do mesmo commit](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/src/main/java/com/github/fmaiassistent/exporter/ClubExporter.java) fornecem esta estrutura:

| Campo | Endereço na RAM descrita pelo projeto |
| --- | --- |
| Ponteiro para bloco de instalações | `club + 0x100` |
| Treino | `facilities + 0x118`, byte |
| Formação | `facilities + 0x123`, byte |
| Treinamento de jovens | `facilities + 0x124`, byte |
| Recrutamento de jovens | `facilities + 0x125`, byte |
| Ponteiro para bloco financeiro | `club + 0x150` |
| Instalações corporativas | `finance + 0x8B5`, byte |

O leitor aceita ratings até 20. Isso é uma regra de plausibilidade, não prova de que qualquer byte 1–20 encontrado seja um rating. Os ponteiros são endereços de memória da plataforma suportada; não podem ser usados como índices no arquivo descomprimido.

O [README do mesmo projeto](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/README.md) exige FM carregado e declara Windows 11/Linux. Portanto, instalar ou executar esse leitor não atende à restrição atual de não acessar o processo, nem oferece uma integração Mac pronta.

## Por que o decoder corporativo não resolve treino/base

O [leitor de instalações do fmsave, commit 34d38551ca4904ae1ef8ffd32f9cf8fb3882385e](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/readers/facilities.py) encontra o fim da cadeia financeira mensal e lê um byte depois dela. O offset varia conforme a quantidade de meses; não se trata de um offset fixo desde o início do clube. O [modelo](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/facilities.py) foi confrontado com a linha Corporate da tela do jogo e declara que não localizou treino, formação ou academia nas proximidades.

No COR `26.3.2+2329565`, o probe local encontrou **528 registros corporativos para 33.884 clubes**, a mesma população das cadeias financeiras disponíveis. Esses 528 registros não são dados de treino/base.

Como controle negativo, foram examinados os bytes `record_start + {0x118, 0x123, 0x124, 0x125}` dos clubes aceitos pelo fmsave. Corinthians, Manchester City masculino, Bayern masculino e Real Madrid devolveram `0,0,0,0`; o segundo registro de City devolveu `231,0,0,0`, e o segundo Bayern, `1,115,0,0`. Isso refuta transferir diretamente os offsets de RAM para o início do registro serializado. Zero não foi publicado como “sem instalações”.

Probe: `/tmp/probe-club-facilities.py`; resumo local: `/tmp/fm-facilities-probe.json`. Ambos são auxiliares desta sessão e não fazem parte do aplicativo ou de sua API.

## Nova trilha: banco estático e nomes dos campos

A instalação local contém `fm.app/Contents/Resources/Data/il2cpp_data/Metadata/global-metadata.dat`. A leitura estática encontrou nomes `TrainingFacilityRating`, `YouthFacilityRating`, `YouthRecruitment`, `YouthFacilitiesStars` e `ClubFacilities`. O binário estático `game_plugin` contém nomes `youth_coaching`, `youth_facilities`, `youth_recruitment` e `corporate_facilities`, além de referências a `CLUB_IN_GAME_DATA` e `CLUB_FINANCE`. Isso confirma vocabulário interno, **não offsets ou valores atuais**. Não foi encontrada uma tabela de serialização aproveitável apenas pelas strings; o exame de símbolos exportados não revelou funções de instalações.

O banco `database/db/2600/2600_fm/server_db.dat` tem contêiner TAD com frames Zstd a partir do byte 38. O probe `/tmp/fm-facilities-db-probe.py` descomprimiu **77 frames**. O frame 3 contém registros de clubes com nomes e IDs, inclusive Corinthians, Manchester City e Bayern, com estrutura semelhante ao cabeçalho do save. Esse material pode auxiliar uma futura comparação estrutural. Seus ratings, se decodificados, seriam valores da base inicial; **não devem substituir instalações atuais da carreira**, que podem melhorar ou degradar.

Nenhum offset anônimo desse banco foi promovido a treino/base. Para fazê-lo, seria necessário demonstrar o campo por uma referência independente (mesmo clube, data e carreira), localizar o mesmo objeto no save e verificar clubes de valores diferentes, incluindo ausência e alteração de instalações. Sem essa ponte, distribuição plausível de bytes não certifica significado.

## Caminhos de dados externos

O `ClubExporter` adicional gera linhas com `trainingFacilities`, `youthFacilities`, `youthCoaching` e `youthRecruitment`. Uma importação de exportação previamente produzida poderia preservar esses dados por snapshot e vincular por ID interno, com nomes na interface. Não foi criada uma importação sem um arquivo real para validar cabeçalhos, identidade da carreira e datas; tampouco foi executado o leitor externo. Esse caminho exigiria mudar a restrição atual de leitura exclusivamente pelo arquivo ou receber uma exportação existente.

O [NG_Regens Savefile Reader Guide](https://ngregens.org/fm26savereader_guide) oferece leitura de saves em Mac, mas documenta identificação de jogadores/staff para geração de rostos. Não fornece decoder ou exportação de instalações, então não é evidência de solução para esse campo. Leitores de EA FC26, Football Manager Mobile e CM03/04 foram excluídos porque seus formatos não são o `.fm` do FM26 desktop.

## Limite atual

Treino, formação, academia, treinamento e recrutamento de jovens continuam sem leitura confiável neste aplicativo. O avanço concreto é identificar o bloco independente na fonte de RAM e uma base estática descomprimível para investigação do correspondente serializado. Nenhum valor foi inventado, associado pelo nome, reutilizado de instalações corporativas ou copiado de ratings iniciais.
