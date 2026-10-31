# Atributos adicionais da comissão técnica

Leitura de 30/10/2026, carreira COR salva em 30/12/2025, build
`26.3.2+2329565`. Fonte SHA-256
`3795481a7bebcdd4512f3c1419b3c0890adda042dc1f5fa74cb73b92874cde8d`.
Foi reutilizado o `game_db` temporário da investigação anterior, sem outra cópia
da carreira, leitura de memória do FM ou alteração do jogo.

O adaptador mantém os campos anteriores e acrescenta autoridade, trabalho com
jovens, determinação e treino de goleiros. São 23 campos profissionais
decodificados: **21 competências entram na soma, com pesos iguais e máximo
420**; dois campos antigos de goleiro permanecem como legado. Adaptabilidade
e os outros sete atributos de personalidade continuam disponíveis separadamente.
Não se trata de afirmar que todos os bytes do editor foram decodificados.

O FM26 apresenta um único atributo de treino de goleiros, confirmado no editor
do jogo e na propriedade `GoalkeepingCoaching` do binário instalado. O próprio
[calculador do FM Scout para FM26](https://www.fmscout.com/f-fm26-coach-rating-calculator.html)
documenta a mudança de três atributos de goleiro para um. Os bytes antigos de
segurar bola e distribuição ainda existem no save, mas sua participação na
qualidade de treino atual não foi demonstrada. Por isso, `gk_handling` e
`gk_distribution` conservam as chaves usadas em filtros e layouts salvos, com
o rótulo `(legado)`, e ficam fora da soma e do placar da comparação. A presença
de um byte antigo não comprova que o FM26 ainda o use como competência.

## Estrutura e escalas

Os offsets abaixo começam em `ability_at`, o mesmo início validado pelo
`fmsave` por UID, tipo, CA/PA, preferências nomeadas, sentinela e extensão do
bloco. Mais de um bloco correspondente continua sendo rejeitado.

| Campo | Offset | Escala armazenada | Conversão |
| --- | --- | --- | --- |
| Autoridade / disciplina | 18 | 1–20 | valor direto |
| Trabalho com jovens | 26 | 1–20 | valor direto |
| Determinação | 27 | 1–100 | `max(1, (valor + 2) // 5)` |
| Treino de goleiros | 41 | 1–100 | mesma conversão |

O [leitor aberto gilet](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/staff.rs)
nomeia esses campos, mas trata a primeira metade como 1–20 apenas nas carreiras
iniciais. Essa suposição não foi aplicada ao bloco inteiro: no COR, autoridade
e jovens estão em 1–20 nas 10.540 linhas com atributos; determinação está em
1–100, com 10.477 valores acima de 20. Uma divisão única para todos esses
campos produziria resultados incorretos.

O nome atual Autoridade corresponde ao antigo Nível de disciplina, conforme o
[changelog do FMRTE 26](https://www.fmrte.com/leaderboard/?time=oldest).
As propriedades `Authority`, `Determination`, `WorkingWithYoungsters`,
`GoalkeepingCoaching` e `Possession` também constam da tabela de nomes do
`global-metadata.dat` do FM instalado. Esses nomes corroboram a nomenclatura;
a presença de uma string isolada não comprova um offset do save.

## Leitura medida

O percurso real do adaptador sobre o cache compartilhado identificou 10.428
pessoas distintas, correspondendo a 10.540 linhas brutas de staff. Todas essas
linhas têm as 23 competências completas. O treinador humano permanece sem
bloco de habilidade demonstrado. A exclusão dos clubes femininos ocorre depois
dessa etapa.

| Profissional | Autoridade | Jovens | Determinação | Goleiros | Soma de 21 |
| --- | --- | --- | --- | --- | --- |
| Célio Silva | 17 | 15 | 18 | 1 | 156 |
| Marko Nikolić | 17 | 11 | 14 | 8 | 235 |
| Daniel Fradley | 9 | 12 | 13 | 7 | 212 |
| Hugo Oliveira | 17 | 13 | 15 | 8 | 204 |
| Unai Emery | 15 | 15 | 15 | 7 | 258 |

Esta tabela documenta o resultado do leitor, não a conferência visual de cada
profissional. A correspondência deve ser conferida no mesmo save; atributos
de uma base inicial ou outra carreira não são substitutos.

A conferência numérica no editor do próprio FM, sem modificar os campos,
confirmou **Célio Silva no Corinthians**, na mesma carreira: Autoridade 17,
Determinação 18, Trabalho com jovens 15, Goleiros 1 e Posse 5. Os cinco valores
coincidem com o leitor; os quatro campos acrescentados estão contemplados
nesse controle. A tela de Pep Guardiola também confirmou os nomes atuais
Autoridade, Posse e Goleiros, mas não foi usada como comparação de bytes:
ele não tem uma linha no conjunto de staff empregado desse cache.

O arredondamento da determinação com frações internas continua usando a
mesma conversão dos atributos escalados; o controle visual de Célio, cujo
valor interno é exatamente 90, não verifica sozinho os casos intermediários.

## Limites e testes

Autoridade e jovens fora de 1–20, ou valores escalados fora de 1–100, permanecem
ausentes. A soma não é calculada quando faltar qualquer competência. Preferências
táticas, personalidade, os dois slots sem nome e o campo genérico `Coaching`
não foram transformados em habilidades adicionais.

Os testes verificam as escalas distintas, arredondamento, ausência, limites,
identidade, CA/PA, preferências, blocos truncados, duplicidade, UIDs alocados
e exclusão dos dois campos legados da soma.
O teste novo falhou com o leitor anterior, que não continha os quatro campos;
após a alteração, `qa.test_staff_skills` e `qa.test_staff_roles` passaram nos
14 casos executados.
