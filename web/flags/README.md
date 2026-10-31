# Bandeiras locais

Assets obtidos em 31/10/2026. O aplicativo usa somente estes arquivos locais;
nenhuma imagem é buscada na internet durante o uso.

- 254 PNGs com 40px de largura: `https://flagcdn.com/w40/{code}.png`.
  Incluem países, territórios e as quatro nações do Reino Unido.
  Catálogo: <https://flagcdn.com/en/codes.json>.
- Fonte e documentação: [FlagCDN / Flagpedia](https://flagpedia.net/download/api).
  O fornecedor descreve a API como gratuita e informa que as imagens são
  baseadas em vetores do Wikimedia Commons. A atribuição ao fornecedor é
  mantida aqui; os símbolos conservam as condições de suas fontes originais.
- `crimea.svg`: [Flag of Crimea](https://commons.wikimedia.org/wiki/File:Flag_of_Crimea.svg),
  original <https://upload.wikimedia.org/wikipedia/commons/a/aa/Flag_of_Crimea.svg>.
  A ficha identifica o desenho de A. Malgin / V. Trusov, a vetorização de
  Madden e a disponibilização do vetor em domínio público.
- `zanzibar.svg`: [Flag of Zanzibar](https://commons.wikimedia.org/wiki/File:Flag_of_Zanzibar.svg),
  original <https://upload.wikimedia.org/wikipedia/commons/d/d4/Flag_of_Zanzibar.svg>.
  Autor indicado: Mysid; disponibilizado em domínio público pelo autor.

`crimea` e `zanzibar` são identificadores internos dos arquivos, não códigos ISO.
Os dois SVGs são os originais estáticos, sem scripts, referências externas,
imagens incorporadas ou elementos `foreignObject`; apenas as quebras de linha
foram normalizadas para LF.

Os PNGs foram limitados a 32KiB por resposta e conferidos como imagens de
40px de largura. Total: 76.567 bytes de PNGs e 580 bytes de SVGs.
