# Cargos atuais do staff: assentos validados do clube

Investigado em 13/10/2026. Foram lidas cópias temporárias de COR; não foi aberto o FM, acessada a memória do processo, alterado o save original ou modificado o leitor instalado.

## Resultado prático

Há uma base para dois cargos exatos, **treinador principal** e **diretor de futebol**, obtidos de assentos do próprio clube e conferidos contra o contrato atual do profissional. Não são inferidos pelo maior atributo, pela área de trabalho ou por seu nome. A lista completa de títulos, incluindo auxiliar, olheiro, chefe de análise, fisioterapeuta e responsáveis de equipes secundárias, continua sem decoder do arquivo demonstrado.

A fonte primária é o [leitor de assentos do gilet](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/backroom.rs) e o [leitor de diretorias](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/club.rs#L114). O gilet documenta Guardiola/City, Arteta/Arsenal e Slot/Liverpool como prova do assento do treinador, com repetição em carreira avançada. Para diretor de futebol, documenta Viana/City e Leca/Lens. São provas externas da estrutura; a nova leitura abaixo verifica a ligação na carreira COR, sem conferir a tela da mesma data.

## Ligação de pessoa: diferença essencial

O assento armazena um **selector**, igual ao `person_id` do header de habilidade mais 1. O UID público do staff é a segunda palavra desse header, usado por `staff_skills.py`. A [descoberta contratual do fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/readers/staff.py) e a [descrição dos layouts](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/_layouts/__init__.py) usam a convenção selector = person_id + 1. Não tratar selector como UID público nem Unique ID.

O primeiro probe, usando diretamente o assento como person_id, obteve 11 ligações no clube correto e **827 no clube errado**. Essa receita foi rejeitada. Aplicando o +1 explícito, houve **2.123 ligações no mesmo clube contratado**, todas únicas por clube e profissional; 98 candidatos que levavam a outro clube foram descartados. Deslocamentos alternativos −3, −2, +1, +2 e +3 produziram apenas 1–5 coincidências de clube. O +1 não deve ser aprendido por nome: já está na convenção do leitor.

Reutilizar o scan de `read_staff_skills`: depois de o header passar UID, CA/PA, preferências, sentinel e limites, obter `person_id = unpack_u32(game_db, header)` e guardar `selector = person_id + 1 -> uid`. Headers conflitantes do mesmo person_id tornam o vínculo ausente. Para cada UID, usar os registros originais completos do staff, pois pode haver mais de um clube. Só aceitar um registro com `has_contract == True` e `club_uid` igual ao assento.

O treinador humano já é explicitamente marcado pelo leitor e não precisa passar pelo bloco de habilidades, de layout diferente.

## Assento do treinador

Dentro de `game_db`, buscar o UID armazenado do clube duplicado seguido de `0a 00`. O UID de clube do fmsave é o armazenado mais 1. A entrada começa quatro bytes antes do primeiro UID.

| Offset desde início da entrada | Conteúdo / validação |
| --- | --- |
| 0 | ordinal da entrada; não é o club_uid |
| 4, 8 | mesmo UID armazenado de clube, diferente de 0 e FFFFFFFF, resolve a clube lido |
| 12, 13 | `0a 00` |
| 25–28 | `FF FF FF FF` |
| 33–36 | selector do treinador; aceitar somente `0 < selector < 3.000.000` |

Exigir que os 37 bytes caibam na seção. O selector precisa resolver de modo único a profissional validado e contratado no mesmo clube. Entradas vazias ou sem ligação segura não atribuem cargo. Se dois profissionais disputarem o mesmo assento de um clube, ambos ficam ausentes; se o mesmo registro obtiver cargos conflitantes, também fica ausente. Repetições idênticas podem ser consolidadas.

No COR, exemplos: Guardiola/Manchester City, Slot/Liverpool e Arteta/Arsenal. A diferença de CA não influencia o cargo.

## Assento do diretor de futebol

Usar `save._context.club_index().record_spans`, já produzido pelo leitor, para permanecer dentro do registro validado do clube. O corpo após os dois nomes fica em:

```python
body = (record_start + club_layout.long_name_offset + 8
        + len(club.name.encode('utf-8')) + len(club.short_name.encode('utf-8')))
```

O layout 26.3.2 tem `long_name_offset = 39`. Os oito bytes são os dois comprimentos u32; contar bytes UTF-8, não caracteres. A forma exata documentada no gilet é:

| Offset desde body | Conteúdo / validação |
| --- | --- |
| 0 | sentinel `01` |
| 1–2 | campo u16 sem nome; não reinterpretado |
| 3–6 | selector do diretor de futebol, 0 ou FFFFFFFF significa vazio |
| 7 | flag de significado não estabelecido; não cria cargo |
| 8 | count da diretoria, no máximo 8 |
| 9… | count selectors u32 de membros da diretoria, cada um em 1…2.999.999 |
| 9 + 4 × count | sentinel final `01` |

Exigir que todo o bloco caiba em `record_end`. O selector do diretor precisa resolver a um único staff contratado no próprio clube, como no treinador. Não converter membros genéricos da diretoria em presidente/owner: não há assento individual identificado para esses títulos. O gilet também exige prova de pessoas não jogadoras para a diretoria; no adaptador proposto, a confirmação do próprio diretor no staff e em seu contrato é a barreira que decide o cargo.

Probe COR: **213 candidatos de diretor de futebol**, e todos os 213 apontaram para contrato do mesmo clube. Exemplos: **Marcelo Paz/Corinthians**, **Richard Hughes/Liverpool**, **Hugo Viana/Manchester City** e **Max Eberl/Bayern**. Nenhum nome foi usado para localizar o assento.

## Por que não basta copiar os offsets de leitores de RAM

O [FMSuperScout](https://github.com/mavarobli/FMSuperScout/blob/b6d6a686a95839bd40d96ac63859144129e9fa4c/plugin/Dumper.cs#L698) lê o cargo da estrutura de contrato **na RAM**, em `contract + 0x26`, e [publica a enumeração personJobTypes](https://github.com/mavarobli/FMSuperScout/blob/b6d6a686a95839bd40d96ac63859144129e9fa4c/plugin/Dumper.cs#L867). O [layout independente do FM AI Assistent](https://github.com/JelmerBouma1985/fm-ai-assistent/blob/12ab90d1ae322103daa218737e20f8729cfc36ef/src/main/java/com/github/fmaiassistent/memory/StaffRecordLayout.java) corrobora `contractJobIdRel = 0x26`. Isso prova que a estrutura viva contém títulos exatos; **não prova que o arquivo serializado tenha o mesmo offset**. Nenhum desses códigos foi aplicado ao save.

`unknown.r4` continua rejeitado como cargo pelo [modelo fmsave](https://github.com/rhiever/fmsave/blob/34d38551ca4904ae1ef8ffd32f9cf8fb3882385e/src/fmsave/models/staff.py#L91): sua comparação de 78 linhas do jogo mostra códigos compartilhando cargos diferentes. O tail contratual também não foi reinterpretado: Guardiola, Slot e Arteta têm `contract_e36 = 3`, enquanto a enumeração de cargo vivo usa Manager = 16. Áreas médicas/coaching/recrutamento permanecem áreas, separadas de títulos exatos.

## Probes e integração mínima

O helper funcional de pesquisa `/tmp/fm_staff_roles_helper.py` recebe bytes de `game_db`, clubes públicos, record_spans e o mapa selector → registros staff criado no scan já validado. Retorna `(staff_uid, club_uid) -> cargo`, com conferência de contrato e rejeição de ambiguidades. Está fora do produto e não tem acesso ao processo do jogo.

Resultados resumidos e exemplos foram serializados em `/tmp/fm-staff-role-helper-results.json`. Esses caminhos temporários não são dependências do aplicativo. Na integração, guardar o status experimental/proveniência dos dois assentos; manter cargos desconhecidos como ausentes e conservar o filtro de área separado. Validar truncamentos, selector/UID alterados, diretorias malformadas, conflito de assento e contrato de outro clube antes de publicar.

A receita depende do formato 26.3.2 e das entradas aceitas pelo leitor atual. Não confere cada título na tela do FM da mesma data; não promete a lista completa de cargos.

O helper passou sete verificações assertivas do probe: assento válido, truncamento em cada um dos 37 cortes possíveis, clube diferente, ausência de contrato, sentinel alterada, corpo com nome UTF-8 e terminador de diretoria alterado. Isso valida o protótipo; os testes do produto ainda precisam cobrir a integração com o scan compartilhado.
