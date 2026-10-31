# Licensing scope

## Original project code and documentation

Original FM Matt Scout source code, tests, scripts, and documentation are offered under the [MIT License](../LICENSE), copyright 2026 Matheus Abrantes, to the extent the project's contributors hold those rights. This includes the project's Python implementation and macOS/web application integration. Existing third-party notices continue to apply to the relevant upstream material.

The standard MIT license text is unchanged. This scope statement identifies material covered by different rights; it does not add restrictions to the MIT grant for original project code or claim exclusive rights over uncopyrightable facts or generated material.

## Upstream code and runtime dependencies

The FMSuperScout-derived valuation equations/rules in `value_model.py` retain copyright 2026 mavarobli and the upstream-declared MIT terms reproduced in [Third-party material](THIRD_PARTY.md). Matt Scout's implementation and integration additions retain their own attribution. Distributions containing that model must preserve both relevant notices.

Separately installed dependencies keep their own licenses. This project's MIT grant does not replace the fmsave MIT license, backports.zstd PSF-2.0 terms, or bundled Zstandard BSD notice. A distribution embedding those packages or Python must carry its actual component notices. Platform frameworks and system fonts remain governed by their providers' terms.

## Data and visual material

The original-code MIT grant does not purport to relicense third-party data or rights embodied in:

- `club-genders.json`, `nation-names.json`, and `league-names.csv`;
- `qa/fixtures/value-model-controls.json`;
- `web/flags/`;
- `docs/assets/` and referenced game/player/club information in documentation or the UI.

Preserve the source records in [Third-party material](THIRD_PARTY.md) and the asset directories. Public-domain flags remain public domain under their source declarations. Factual identifiers, names, and numeric observations do not acquire a new proprietary restriction merely by appearing here. No license is granted on behalf of Football Manager, Sports Interactive, SEGA, Footyshoe, or another third-party rightsholder.

`club-genders.json` retains its [documented Footyshoe provenance](CLUB_GENDERS.md). Permission for public redistribution of the systematic extraction remains unverified. The maintainer has decided to retain the reference and accepts that residual publication risk. Neither this decision nor exclusion from the MIT grant establishes third-party redistribution permission. See the [recorded source-publication assessment](PUBLIC_RELEASE.md).

Requests from legitimate rights holders will be reviewed promptly. Affected material will be removed or replaced where appropriate.

## Names and trademarks

Product, organization, club, and competition names identify compatibility or describe data. The MIT grant does not authorize use of another party's trademarks or imply endorsement. FM Matt Scout remains an independent project.
