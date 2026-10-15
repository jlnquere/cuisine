#!/usr/bin/env python3
"""Export Cuisine into Quartz without changing the source vault."""
import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse

parser = argparse.ArgumentParser()
parser.add_argument('--vault', type=Path, default=Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Foundation')
args = parser.parse_args()
source = args.vault / '10 Workspaces/Perso/Cuisine'
root = Path(__file__).resolve().parents[1]
target = root / 'content'
if not source.is_dir():
    raise SystemExit(f'Dossier introuvable : {source}')
files = [p for p in source.rglob('*') if p.is_file() and not any(x.startswith('.') for x in p.relative_to(source).parts)]
notes = [p for p in files if p.suffix == '.md' and not p.name.startswith('README') and p.name != 'Recettes - Index.md']
norm = lambda s: unicodedata.normalize('NFC', s)
lookup = {}
for p in files:
    rel = p.relative_to(source).as_posix()
    keys = [rel, str(p.relative_to(args.vault)), p.name, p.stem if p.suffix == '.md' else p.name]
    keys.extend('/'.join(p.relative_to(source).parts[i:]) for i in range(1, len(p.relative_to(source).parts)))
    for key in keys:
        lookup.setdefault(norm(key.removesuffix('.md')), []).append(p)
missing = []
external = []
used_assets = set()

def rewrite(match):
    original = match.group(1)
    path, sep, label = original.partition('|')
    path, anchor_sep, anchor = path.partition('#')
    if not path:
        return match.group(0)
    candidates = set(lookup.get(norm(path.removesuffix('.md')), []))
    if len(candidates) != 1:
        (missing if Path(path).suffix else external).append(original)
        return (label or Path(path).stem) if not match.group(0).startswith('!') else ''
    p = candidates.pop()
    if p.suffix == '.md' and p not in notes:
        return label or p.stem
    if p.suffix != '.md':
        used_assets.add(p)
    rel = norm(p.relative_to(source).as_posix()).removesuffix('.md')
    return ('!' if match.group(0).startswith('!') else '') + '[[' + rel + (('#' + anchor) if anchor_sep else '') + (('|' + label) if sep else '') + ']]'

rendered = {}
def markdown_to_wiki(match):
    image, label, link = match.groups()
    if urlparse(link).scheme or link.startswith(('#', '//')):
        return match.group(0)
    return image + '[[' + unquote(link) + ('|' + label if label else '') + ']]'

for p in notes:
    text = re.sub(r'(!?)\[([^\]]*)\]\(([^)\n]+)\)', markdown_to_wiki, p.read_text())
    rendered[norm(p.relative_to(source).as_posix())] = re.sub(r'!?\[\[([^\]]+)\]\]', rewrite, text)
if missing:
    (root / 'import-report.json').write_text(json.dumps({'unresolved_links': sorted(set(missing))}, ensure_ascii=False, indent=2))
    raise SystemExit('Liens non résolus : consulter import-report.json. Export précédent conservé.')
staging = root / '.cuisine-export'
if staging.exists():
    shutil.rmtree(staging)
staging.mkdir()
for rel, text in rendered.items():
    out = staging / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
for p in used_assets:
    out = staging / norm(p.relative_to(source).as_posix())
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, out)
for folder, title in [('Recettes', 'Recettes'), ('Techniques', 'Techniques de cuisine')]:
    paths = sorted((p for p in notes if p.relative_to(source).parts[0] == folder), key=lambda p: norm(p.stem).casefold())
    links = '\n'.join('- [[' + norm(p.relative_to(source).as_posix()).removesuffix('.md') + '|' + norm(p.stem) + ']]' for p in paths)
    (staging / folder / 'index.md').write_text(f'---\ntitle: {title}\n---\n\n{links}\n')
(staging / 'index.md').write_text('---\ntitle: Cuisine\n---\n\nDes recettes et des gestes à retrouver au moment de cuisiner.\n\n- [[Recettes/index|Parcourir les recettes]]\n- [[Techniques/index|Apprendre les techniques]]\n\nUtilisez la recherche pour retrouver un plat ou un ingrédient.\n')
if target.exists():
    shutil.rmtree(target)
staging.rename(target)
report = {'notes': len(notes), 'images': len(used_assets), 'unresolved_links': [], 'outside_cuisine_links_as_text': sorted(set(external))}
(root / 'import-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False))
