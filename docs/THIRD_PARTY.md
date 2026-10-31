# Third-party material

Provenance reviewed on 31 October 2026. FM Matt Scout's own source and third-party material have separate rights. The [MIT license](../LICENSE) for original project code does not relicense another owner's data, images, trademarks, or software. See [licensing scope](LICENSING.md).

## Runtime dependencies

| Component | Use and terms |
| --- | --- |
| [fmsave 0.5.10](https://github.com/rhiever/fmsave/tree/v0.5.10) | Save parsing. [MIT license](https://github.com/rhiever/fmsave/blob/v0.5.10/LICENSE), copyright 2026 Randal S. Olson. Pinned in `requirements.txt`. |
| [backports.zstd](https://github.com/rhiever/fmsave/blob/v0.5.10/pyproject.toml) | Conditional fmsave dependency on Python below 3.14. Installed 1.8.0 declares PSF-2.0 and includes the BSD notice for bundled Zstandard. Its version is resolved by pip. |
| Apple AppKit / WebKit | macOS platform frameworks, not vendored framework source. |

The Python packages are installed separately, and the local app ZIP does not bundle its `.venv`. A future package that embeds Python or its dependencies must retain the applicable runtime/package notices. None of these dependency terms requires changing the original Matt Scout source to a different license.

## FMSuperScout valuation model

`value_model.py` adapts the equations and decision rules published in [FMSuperScout at revision cd0062e](https://github.com/mavarobli/FMSuperScout/blob/cd0062e0e51ca57bbed5ef0268a04427e3655afd/app/app.js#L1027-L1140). The Python implementation adds Matt Scout's input validation, save integration, missing-data handling, and documented adaptations. It is not represented as a clean-room implementation with no upstream influence. See [model research](PLAYER_VALUES_RESEARCH.md).

The pinned upstream [manifest declares MIT](https://github.com/mavarobli/FMSuperScout/blob/cd0062e0e51ca57bbed5ef0268a04427e3655afd/package.json); its [installer identifies copyright 2026 mavarobli](https://github.com/mavarobli/FMSuperScout/blob/cd0062e0e51ca57bbed5ef0268a04427e3655afd/installer/FMSuperScout.iss#L41). The reviewed revision has no standalone project LICENSE file. The notice below reproduces the standard license identified by that declaration, preserving the verified upstream copyright. The separate BepInEx notice in the upstream installer applies to that unrelated component.

Retain this attribution and notice when distributing the adapted model. Original Matt Scout additions remain separately attributable to this project.

```text
MIT License

Copyright (c) 2026 mavarobli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Data and reader research

| Local material | Provenance and disposition |
| --- | --- |
| `nation-names.json` | The 228 factual code/name associations from [gilet's nation map](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/person.rs), localized into Portuguese in a JSON lookup. No Rust implementation is included. Retain the source credit; see [names](NAMES.md). |
| `staff_skills.py` | Local Python adapter informed by gilet's [staff layout research](https://github.com/fifteen15-labs/gilet/blob/716bfc80fdabc6ab88be4e4908d9738ffc346b69/crates/fm-save/src/staff.rs). Shared offsets, field order, and conversion rules describe the save format; local scanning, validation, and integration are project implementation. [Staff research](STAFF_READER_RESEARCH.md) records checks and scale differences. No upstream module is vendored. |
| Staff job-code references | [FM AI Assistent](https://github.com/JelmerBouma1985/fm-ai-assistent) informed factual code-name research, not a runtime dependency or copied Java module. |
| `league-names.csv` | A selected 56-row factual ID/name lookup from the locally installed game's competition table; not a redistributed complete table. See [names](NAMES.md). |
| `qa/fixtures/value-model-controls.json` | Eight locally observed save/game controls, packaged for the project's regression checks. These are selected numeric observations, not an imported upstream fixture or full database. See [valuation research](PLAYER_VALUES_RESEARCH.md). |
| `club-genders.json` | ID/category pairs extracted from [Footyshoe](https://footyshoe.com/), including 1,499 female-club IDs across 38 pages and 40 male IDs. Public redistribution permission for that systematic extraction remains unverified. The maintainer retains this reference with attribution and accepts the residual publication risk; this decision is not a redistribution grant. See [collection method and functional effect](CLUB_GENDERS.md). |

The factual-map, reader-format, selected-name, and eight-control findings are closed as informational within the inspected scope; a missing license in a research reference does not by itself establish that Matt Scout copied protected program expression. This does not grant rights in a complete game or third-party database. The bulk Footyshoe extraction is retained under the maintainer's recorded acceptance of residual risk: no applicable reuse grant or prohibition was established. Attribution, the MIT exclusion, and the maintainer's decision do not establish redistribution permission. Requests from legitimate rights holders will be reviewed promptly, with removal or replacement where appropriate.

## Flags, design, and screenshots

The 254 PNG flags from FlagCDN/Flagpedia and two SVG flags from Wikimedia Commons have documented public-domain sources. Keep the [asset record](../web/flags/README.md), [Flagpedia terms](https://flagpedia.net/terms), and Commons records for [Crimea](https://commons.wikimedia.org/wiki/File:Flag_of_Crimea.svg) and [Zanzibar](https://commons.wikimedia.org/wiki/File:Flag_of_Zanzibar.svg). This does not resolve separate local rules about official symbols.

[DESIGN.md](../DESIGN.md), `web/app.js`, and `web/style.css` implement an owner-commissioned Claude Design prototype and specification for FM Matt Scout. Visual tokens, layout, and inline control SVGs were adapted from that export; application data flow and production behavior were integrated locally. No external template or icon-library dependency was identified. System fonts are used; no font files or prototype runtime are shipped. This provenance finding is closed; it is not a claim of exclusive rights over every generated shape or generic UI convention.

[README screenshots](assets/README.md) show the actual application with real career data, including light and dark modes. They contain no player photographs or official club crests. Referenced game names, data, and trademarks remain outside any original-code license grant. No complete game database, game save, or official FM/SI/SEGA/Genie logo is included in the original tracked assets.

## References and independence

[REA](https://github.com/morluto/rea/blob/main/README.md) and [CodexBar](https://github.com/steipete/CodexBar/blob/main/README.md) informed documentation presentation; their text, branding, and images were not reused. FM Genie Scout is a functional inspiration, not the source of Matt Scout's rating formula. Football Manager, Sports Interactive, SEGA, and other referenced names belong to their respective owners.
