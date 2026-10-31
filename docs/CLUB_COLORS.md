# Cores dos clubes no FM26

`club_colors.py` lê as duas cores ARGB da base instalada do jogo. O save fornece
o identificador do clube; não há uma lista de paletas por nome no aplicativo.
A base e os saves continuam locais e não são distribuídos com o código.

## Identidade e formato conferidos

- Build de origem: `26.3.2+2329565`, schema `game_db` 4000.
- O início do registro próprio contém ordinal, UID e cópia do UID. O rodapé
  contém o próximo ordinal e duas cópias do identificador da base. Exigem-se
  ordinal consecutivo, UID compatível, limites válidos e donos únicos.
- Esse identificador difere de `unique_id` em parte dos registros aceitos pelo
  leitor. A associação não usa o nome nem o próximo clube aceito como dono.
- `client_db.dat` tem prefixo `tad.` de 12 bytes e contêiner FMF. Só são lidas
  `table_3.dat` e `table_extra_3.dat`, com limite conjunto de 64 MiB.
- `table_3` associa ordinal ao identificador; o prefixo `0x0c` acrescenta quatro
  bytes antes do rodapé. `table_extra_3` usa o mesmo ordinal e termina cada
  registro com fundo ARGB e texto ARGB, após os uniformes de 27 bytes.
- Tabelas completas, schema, contagens, duplicações, UTF-8, rodapés e fim do
  arquivo são validados. Só pares com alpha 255 são aceitos.
- A versão de origem da carreira tem prioridade: `26.2.0+0` usa 2620 antes de
  2600. A outra base preenche apenas identificadores ainda sem paleta válida.

## Evidência no COR

Foram obtidas **31.653 paletas em 32.867 clubes visíveis (96,3%)**, todas da
base 2620. Os outros 1.211 registros associados têm os dois ARGB zerados;
três clubes não têm dono estrutural confirmado. Nesses casos o badge é neutro.

| Controle | ID da base | Fundo | Texto original |
| --- | ---: | --- | --- |
| Corinthians | 319 | #1E2021 | #FFE252 |
| Arsenal | 602 | #E20613 | #FAFAFA |
| Chelsea | 630 | #001489 | #FAFAFA |
| Liverpool | 676 | #D10011 | #FAFAFA |
| Man City | 679 | #7AB2E1 | #FAFAFA |
| Bayern München | 915 | #ED0037 | #FFFFFF |
| Barcelona | 1708 | #1D3C72 | #DD004A |
| Real Madrid | 1736 | #FAFAFA | #17285C |

O frontend preserva o fundo e troca apenas a cor do texto por branco/preto se
o par tiver contraste abaixo de 4,5:1. A paleta original continua na API.
Não se infere uma paleta dos uniformes quando as cores estão zeradas.

Seis testes em `qa/test_club_colors.py` cobrem identidade, limites, duplicações,
versões, tabelas completas/truncadas e instalação ausente. A suíte de interface
confere cores da API no DOM, incluindo clubes fora dos 12 do protótipo.

O suporte a outro build/schema exige nova conferência. As cores vêm da base
instalada, não de alterações de cores específicas da carreira nem da memória
do processo do jogo. Sem uma instalação compatível, o restante do app funciona
e os badges permanecem neutros.
