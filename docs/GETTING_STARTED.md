# Setup and development

FM Matt Scout is a development preview for macOS. There is no published standalone installer. The current app uses AppKit and WebKit; the browser interface is also useful for local development. Its labels are currently in Portuguese.

## Requirements

- macOS for the native application. The bundle declares macOS 13.0, but the Swift build does not set an explicit deployment target. Runtime compatibility with older macOS versions still needs testing.
- Python 3.12 or newer for `fmsave`; the native build script specifically expects Python 3.12 at `/opt/homebrew/bin/python3.12` when creating its environment.
- Git. Apple's Command Line Tools, including `xcrun swiftc`, are also needed for the native app.
- Your own Football Manager 26 `.fm` save. Additional readers have been checked against build `26.3.2+2329565`; other builds may have different coverage.

The current native workflow assumes an Apple Silicon Homebrew installation. It produces a host-architecture binary; Intel and universal builds have not been validated. There is no iOS application.

## Run the local browser interface

Clone the repository once you have access, then create its Python environment:

```sh
git clone https://github.com/matheusabrantes/fm-matt-scout.git
cd fm-matt-scout
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python server.py
```

Open the **complete URL printed by the server** in a local browser. The address contains a random access token and changes on each launch. Keep it out of public logs and screenshots. Press Control-C in the terminal to stop the server.

This is the existing web interface without the native file dialogs. Choose a discovered save or enter its full `.fm` path in the welcome screen. No running game is needed. Save the career in FM before loading it, and wait for any save operation to finish.

For a separate development data directory:

```sh
mkdir -p local-data
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python server.py --storage local-data/scout.sqlite3
```

`--storage` also places JSON preferences beside that database. It does not change the standard folder used to discover saves.

## Build the native macOS app

First close any running FM Matt Scout application. Check that `xcrun --find swiftc` and `/opt/homebrew/bin/python3.12 --version` work, then run:

```sh
./build.command
open "/Applications/FM Matt Scout.app"
```

The script installs Python dependencies, **replaces `/Applications/FM Matt Scout.app`**, registers the app with macOS, and writes `dist/FM Matt Scout.zip`. It applies an ad hoc signature to the generated bundle. This is a local developer workflow; Developer ID signing and notarization have not been prepared.

The app and ZIP reference the `.venv` at the checkout's exact path. Keep the checkout and environment in place. Rebuild after moving them or changing the application code. The ZIP is a local build artifact, not a portable installer.

## First use

1. Open your career through **Open Save…** (Command-O) or the welcome screen.
2. Use **Jogadores**, **Staff**, or **Clubes** in the sidebar. Search, sort a column, or open **Filtros** to narrow the results.
3. Click a name for its profile. Select two players or two staff members and choose **Comparar** for a comparison.
4. Add records to **Minha lista** to keep a shortlist for that career.
5. Use the save card's **Moeda / salários…** settings to check currency conversion against a value in your own game. Until then, numbers may be shown in raw save units.

The original save is copied to a temporary directory for parsing. The app does not edit it. Saves and app data are processed locally; the inspected application flow has no cloud upload.

## Local data

By default, app data lives in `~/Library/Application Support/FM Matt Scout/`:

| File | Contents |
| --- | --- |
| `scout.sqlite3` | Career shortlists and player-history snapshots |
| `filters.json` | Named searches and filter presets |
| `layouts.json` | Visible columns and widths |
| `salaries.json` | Per-career currency and salary calibration |

Keep your data backed up. History and shortlists use the save's path as the career identity, so moving a save starts a separate history. Reloading a career records the first snapshot for each loaded in-game date; it cannot recover dates you never loaded.

## Checks

These checks use the installed Python environment and synthetic/unit fixtures:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s qa -p 'test_*.py' -v
node qa/check_money_fields.cjs
node qa/check_theme.cjs
```

The browser integration harnesses in `qa/check_redesign.cjs` and `qa/check_flags.cjs` currently refer to the original developer's Playwright installation and a named local save. They need local adaptation before use on another machine. `qa/check_ui.cjs` retains the earlier navigation flow. These scripts are not clean-clone CI instructions.

`qa/check_save.py` explicitly reads the `.fm` file supplied as its argument and verifies that its bytes remain unchanged. Run it only with a career you intend to inspect. See [QA records](QA.md) for historical results; they are dated evidence, not a new validation of every machine or game build.

## Troubleshooting

- **Python not found:** the native script's bootstrap path is fixed. Use the browser workflow with an available Python 3.12+ interpreter, or review a separate build-script change before adapting it for another installation.
- **App cannot start its reader:** check that the checkout and `.venv` still exist at the build-time path. Rebuild after moving them.
- **Empty or incomplete fields:** check the [coverage notes](COVERAGE.md) and game build. Unknown values remain unavailable; they are not automatically zero.
- **Money differs from FM:** check the currency, salary period, and per-career reference. Abbreviated in-game values produce approximate calibration.
- **Save changes during loading:** wait for FM to finish saving, then retry. The reader rejects a source that changes while its temporary copy is being made.

Do not disable Gatekeeper or other macOS security controls to install a shared ZIP. A general distribution and signing workflow remains future work.
