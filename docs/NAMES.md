# Nomes na pesquisa

A interface pesquisa nomes e mantém os códigos apenas nas ligações internas e arquivos de filtros. Nacionalidades, países, clubes e movimentos não exigem conhecer um ID. A coluna de país ordena pelo nome, com nomes ausentes no fim.

`nation-names.json` contém 228 correspondências factuais entre o código interno do save e país/federação, traduzidas para português. Fonte: [mapa de nações do leitor gilet](https://github.com/fifteen15-labs/gilet/blob/main/crates/fm-save/src/person.rs), função `nation_name`; [método de identificação](https://github.com/fifteen15-labs/gilet/blob/main/docs/SAVE_FORMAT.md). Esse espaço de códigos difere dos IDs exibidos no editor.

Os códigos de Brasil, Portugal, Inglaterra, França, Alemanha e Argentina foram conferidos contra os agrupamentos de clubes do save COR. Isso verifica a compatibilidade do mapa com essa carreira; não substitui a validação de cada campo de nacionalidade na tela do jogo. País desconhecido aparece como “Nome indisponível” no perfil/tabela e não vira opção numérica.

Na tela do FM aberto, Vinícius Júnior exibiu Brasileiro/Espanhol. O mesmo jogador no save tem Brasil/Espanha (principal/adicional), confirmando esse exemplo com o jogo. Essa leitura não confirma todos os 228 nomes do mapa.

As competições continuam precisando de um mapa próprio, já suportado pelo leitor, e do vínculo com a divisão atual do clube. Nenhum nome é deduzido pela composição de uma tabela: isso poderia confundir divisões, copas e fases. O filtro mostra “Liga do clube ainda não identificada” até esse vínculo ser decodificado. Filtros antigos conservam os códigos internos para não perder critérios, mas opções sem nome mostram “Opção salva indisponível”; um código de copa não passa pelo filtro de liga atual.

As regiões usam a classificação geográfica [UN M49](https://unstats.un.org/unsd/methodology/m49/), agrupando América do Norte, Central e Caribe num seletor. Guiana e Suriname ficam na América do Sul; Israel, Chipre e Turquia na Ásia, independentemente da confederação esportiva. As federações britânicas usam Europa; Kosovo e Crimeia usam Europa; Taiti usa Oceania e Zanzibar usa África. Essas adaptações cobrem as entidades usadas pelo FM que não têm entrada geográfica própria na M49. A região onde atua usa o país da liga do clube lido pelo fmsave, e não uma localização física independente; sem vínculo de clube/país, ela permanece ausente.

`.fmf` é um formato de arquivos do Football Manager, usado também para listas importáveis no jogo. A exportação `.fmf` de shortlist ainda não está implementada; os JSON de filtros/listas são formatos do Matt Scout.

Nacionalidades são a união da principal com `second_nation_ids`, sem duplicatas. Região da nacionalidade e filtro UE pesquisam essa mesma união. `home_grown_nation_ids` indica formação no país e não entra como cidadania. País/região onde atua permanece ligado ao clube. Staff usa as nacionalidades efetivamente disponíveis no leitor, que atualmente entrega apenas sua nacionalidade principal.

Os membros da UE foram conferidos na [lista oficial da União Europeia](https://european-union.europa.eu/principles-countries-history/eu-countries_en) em 12/10/2026. A classificação cobre os 27 países atuais; Reino Unido, Noruega e Suíça não são membros. No perfil, cada cidadania membro recebe “UE”. Ter uma nacionalidade UE não comprova todas as regras de inscrição de uma liga no FM. Se nenhuma nacionalidade for UE e algum país não puder ser identificado, o indicador é Indisponível; não é convertido em Não.
