#!/bin/zsh
set -eu
cd "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  /opt/homebrew/bin/python3.12 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
app_dir="/Applications/FM Matt Scout.app"
mkdir -p "$app_dir/Contents/MacOS" "$app_dir/Contents/Resources"
xcrun swiftc macos/App.swift -O -framework AppKit -framework WebKit -o "$app_dir/Contents/MacOS/FMMattScout"
cp scout.py server.py presets.py salaries.py staff_skills.py staff_roles.py "$app_dir/Contents/Resources/"
cp league-names.csv "$app_dir/Contents/Resources/"
cp nation-names.json "$app_dir/Contents/Resources/"
cp club-genders.json "$app_dir/Contents/Resources/"
rm -rf "$app_dir/Contents/Resources/__pycache__"
cp -R web "$app_dir/Contents/Resources/"
if [[ -f competition-names.csv ]]; then cp competition-names.csv "$app_dir/Contents/Resources/"; fi
.venv/bin/python - "$app_dir" "$PWD/.venv/bin/python" <<'PY'
import plistlib, sys
from pathlib import Path
app, python = sys.argv[1:]
info = {'CFBundleExecutable':'FMMattScout','CFBundleIdentifier':'br.com.matt.fm-scout',
        'CFBundleName':'FM Matt Scout','CFBundleDisplayName':'FM Matt Scout 26',
        'CFBundlePackageType':'APPL','CFBundleShortVersionString':'0.1.0',
        'CFBundleVersion':'1','LSMinimumSystemVersion':'13.0',
        'NSHighResolutionCapable':True,'MattScoutPython':python}
with (Path(app)/'Contents/Info.plist').open('wb') as f: plistlib.dump(info,f)
PY
xattr -cr "$app_dir"
codesign --force --deep --sign - "$app_dir"
xattr -cr "$app_dir"
codesign --verify --deep --strict "$app_dir"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$app_dir"
mkdir -p dist
ditto -c -k --keepParent --norsrc --noextattr "$app_dir" "$PWD/dist/FM Matt Scout.zip"
print "Aplicativo criado: $app_dir"
print "Arquivo criado: $PWD/dist/FM Matt Scout.zip"
