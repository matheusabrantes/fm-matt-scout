# Public release review

**Assessment: READY FOR PUBLICATION (source), with accepted residual risk** · 31 October 2026

This assessment records completion of the source review within the inspected scope and the maintainer's decisions below. It is not a guarantee of legal clearance or third-party permission. Publication still requires separate authorization; no commit, push, visibility change, or release has occurred.

## Adopted decisions

| Item | Recorded decision |
| --- | --- |
| Original-code license | Standard [MIT license](../LICENSE), copyright 2026 Matheus Abrantes, for original project source and documentation. [Licensing scope](LICENSING.md) preserves third-party rights and notices. |
| `club-genders.json` | Retain the existing Footyshoe reference and accurate attribution. Public redistribution permission for its systematic extraction remains unverified; the maintainer understands and accepts that residual publication risk. No infringement was established by the inspected evidence. |

The Footyshoe decision is risk acceptance, not a redistribution grant or a finding that no applicable rights exist. The data, provenance, and application behavior remain unchanged. Requests from legitimate rights holders will be reviewed promptly, with removal or replacement of affected material where appropriate.

## Resolved provenance findings

- `nation-names.json`: translated factual identifier/name map; no copied Rust implementation.
- `staff_skills.py`: local Python implementation using documented format facts and independent checks.
- `league-names.csv`: a selected factual names lookup, not the complete game table.
- `qa/fixtures/value-model-controls.json`: eight locally observed controls in an original regression fixture.
- `value_model.py`: upstream MIT declaration and copyright verified; adaptation credit and full notice retained in [Third-party material](THIRD_PARTY.md).
- `DESIGN.md`, `web/app.js`, and `web/style.css`: owner-commissioned design export and local production integration, with no identified external template or icon-library dependency.
- Runtime dependencies and flags: identified compatible terms/provenance, with their own rights preserved.

These are evidence-based conclusions within the inspected scope, not a guarantee of universal originality or clearance of every game/database use.

## Security and documentation

The earlier local credential/history audit found no confirmed exposed credential, private key, or sensitive authentication file. That bounded result is unchanged; this licensing update did not repeat the full security audit. Detailed evidence remains outside the publishable repository.

The README presents the implemented macOS application, authentic career screenshots, a source-based developer workflow, and actual compatibility/distribution limits. The setup guide discloses the native build's replacement of the installed app and its dependency on the checkout. Local data, environment files, signing material, and generated packages remain ignored.

## Scope of readiness

No new concrete source-publication blocker was identified in applying the approved licensing documentation. The previously outstanding owner decisions are now recorded. The residual Footyshoe uncertainty remains disclosed; the maintainer's acceptance does not bind a rights holder.

Binary distribution is a separate future task: the current ZIP is not standalone or notarized. A packaged runtime needs its component notices and testing for the claimed macOS versions/architectures. This source assessment does not authorize a binary release or a change to repository visibility.
