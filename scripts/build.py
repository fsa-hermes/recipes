#!/usr/bin/env python3
"""
Générateur de site statique pour le livre de recettes — version SPA minimaliste.
"""
import os
import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content" / "recettes.md"
OUTPUT = ROOT / "index.html"

ICONS = {
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>',
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    'salad': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
    'main': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>',
    'dessert': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
    'side': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M9 9h6v6H9z"></path></svg>',
    'drink': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 22h8"></path><path d="M12 11v11"></path><path d="M7 11a5 5 0 0 1 10 0v7"></path></svg>',
    'default': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>',
    'source': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
}

CSS = r"""
:root {
  --bg: #fafafa;
  --fg: #1a1a1a;
  --fg-muted: #6b6b6b;
  --accent: #c0392b;
  --accent-hover: #a93226;
  --card: #ffffff;
  --border: #eee;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --radius: 10px;
  --radius-sm: 6px;
  --sidebar-w: 260px;
  --header-h: 56px;
  --transition: 160ms ease;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.6;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.app { display: grid; grid-template-columns: var(--sidebar-w) 1fr; grid-template-rows: var(--header-h) 1fr; height: 100vh; overflow: hidden; }
.header { grid-column: 1 / -1; background: var(--card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; position: sticky; top: 0; z-index: 100; box-shadow: var(--shadow); }
.header-left { display: flex; align-items: center; gap: 1rem; }
.logo { font-size: 1.15rem; font-weight: 600; color: var(--accent); letter-spacing: -0.02em; text-decoration: none; }
.search-box { position: relative; width: 280px; }
.search-box input { width: 100%; padding: 0.5rem 1rem 0.5rem 2.5rem; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.9rem; background: var(--bg); color: var(--fg); transition: border-color var(--transition), box-shadow var(--transition); }
.search-box input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.15); }
.search-box svg { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 18px; height: 18px; stroke: var(--fg-muted); pointer-events: none; }
.header-right { display: flex; align-items: center; gap: 0.75rem; }
.btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all var(--transition); text-decoration: none; background: var(--card); color: var(--fg); }
.btn:hover { background: var(--bg); border-color: #ddd; }
.btn-primary { background: var(--accent); border-color: var(--accent); color: white; }
.btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
.btn svg { width: 16px; height: 16px; }
.sidebar { background: var(--card); border-right: 1px solid var(--border); overflow-y: auto; padding: 1.5rem 1rem; position: sticky; top: var(--header-h); height: calc(100vh - var(--header-h)); }
.sidebar-section { margin-bottom: 2rem; }
.sidebar-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--fg-muted); margin-bottom: 0.75rem; font-weight: 600; }
.category-list { list-style: none; }
.category-item { display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); cursor: pointer; transition: background var(--transition); color: var(--fg); text-decoration: none; font-size: 0.95rem; }
.category-item:hover { background: var(--bg); }
.category-item.active { background: #fef2f2; color: var(--accent); font-weight: 500; }
.category-icon { width: 18px; height: 18px; flex-shrink: 0; stroke: currentColor; }
.category-count { margin-left: auto; font-size: 0.75rem; color: var(--fg-muted); background: var(--bg); padding: 0.1rem 0.5rem; border-radius: 999px; }
.category-item.active .category-count { background: #fecaca; color: var(--accent); }
.main { overflow-y: auto; padding: 2rem; background: var(--bg); }
.main-header { margin-bottom: 2rem; }
.main-title { font-size: 1.5rem; font-weight: 600; color: var(--fg); margin-bottom: 0.25rem; }
.main-subtitle { color: var(--fg-muted); font-size: 0.95rem; }
.recipes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.25rem; }
.recipe-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow); transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition); display: flex; flex-direction: column; }
.recipe-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); border-color: #e0e0e0; }
.recipe-card.hidden { display: none; }
.recipe-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 1rem 1.25rem 0; }
.recipe-name { font-size: 1.1rem; font-weight: 600; color: var(--fg); line-height: 1.3; }
.recipe-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0 1.25rem 1rem; }
.tag { font-size: 0.7rem; font-weight: 500; padding: 0.2rem 0.55rem; border-radius: 999px; white-space: nowrap; border: 1px solid transparent; }
.tag-category { background: #fff3e0; color: #e65100; border-color: #ffe0b2; }
.tag-difficulty-facile { background: #e8f5e9; color: #2e7d32; border-color: #c8e6c9; }
.tag-difficulty-moyenne { background: #fff3e0; color: #e65100; border-color: #ffe0b2; }
.tag-difficulty-difficile { background: #ffebee; color: #c62828; border-color: #ffcdd2; }
.tag-time { background: #f5f5f5; color: var(--fg-muted); border-color: var(--border); }
.tag-portions { background: #e3f2fd; color: #1565c0; border-color: #bbdefb; }
.tag-cost { background: #fce4ec; color: #c2185b; border-color: #f8bbd0; }
.recipe-divider { height: 1px; background: var(--border); margin: 0.25rem 1.25rem 0.75rem; }
.recipe-body { padding: 0 1.25rem 1.25rem; flex: 1; display: flex; flex-direction: column; }
.recipe-section { margin-bottom: 1rem; }
.recipe-section-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--fg-muted); margin-bottom: 0.5rem; font-weight: 600; }
.ingredients-list { columns: 2; column-gap: 1.5rem; font-size: 0.85rem; }
.ingredients-list li { break-inside: avoid; margin-bottom: 0.3rem; padding-left: 0.5rem; border-left: 2px solid transparent; }
.ingredients-list li:hover { border-left-color: var(--accent); }
.steps-list { counter-reset: step; font-size: 0.85rem; }
.steps-list li { list-style: none; position: relative; padding-left: 1.75rem; margin-bottom: 0.6rem; line-height: 1.5; }
.steps-list li::before { counter-increment: step; content: counter(step); position: absolute; left: 0; top: 0; width: 1.25rem; height: 1.25rem; background: var(--accent); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 600; flex-shrink: 0; }
.recipe-notes { margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--fg-muted); }
.recipe-notes summary { cursor: pointer; font-weight: 500; color: var(--fg); margin-bottom: 0.4rem; }
.recipe-notes ul { margin-left: 1rem; }
.recipe-notes li { margin-bottom: 0.2rem; }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 4rem 2rem; color: var(--fg-muted); }
.empty-state svg { width: 64px; height: 64px; margin-bottom: 1rem; opacity: 0.5; }
@media (max-width: 900px) { .app { grid-template-columns: 1fr; grid-template-rows: var(--header-h) auto 1fr; } .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); padding: 1rem; display: none; } .sidebar.open { display: block; } .main { padding: 1.5rem 1rem; } .recipes-grid { grid-template-columns: 1fr; } .search-box { width: 100%; max-width: 300px; } .header-right .btn-text { display: none; } }
@media (max-width: 600px) { .ingredients-list { columns: 1; } .header { padding: 0 1rem; } .main { padding: 1rem; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.recipe-card { animation: fadeIn 0.3s ease both; }
"""

# Read JS from separate file to avoid escaping issues
JS_FILE = ROOT / "scripts" / "app.js"

def parse_recipes(md_text):
    recettes_match = re.search(r'\n## Recettes\n', md_text)
    if not recettes_match:
        return []
    content_after_recettes = md_text[recettes_match.end():]
    parts = re.split(r'\n###\s+(?=[🧀🥘🍳🍲🥗🍝🍕🍔🌮🍣🍤🍛🍜🍚🥞🧁🍰🍪🍩🍫🍬🍭🍮🍦🍨🍧🥧🍯🥛☕🍵🍶🍺🍻🥂🍷🥃🍸🍹🍾])', content_after_recettes)
    recipes = []
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split('\n')
        if not lines:
            continue
        name = lines[0].strip()
        if name.lower() in ('ingrédients', 'ingredients', 'préparation', 'preparation', 'notes'):
            continue
        name = re.sub(r'^###\s*', '', name)
        name = re.sub(r'^[🧀🥘🍳🍲🥗🍝🍕🍔🌮🍣🍤🍛🍜🍚🥞🧁🍰🍪🍩🍫🍬🍭🍮🍦🍨🍧🥧🍯🥛☕🍵🍶🍺🍻🥂🍷🥃🍸🍹🍾]\s*', '', name)
        recipe = {'name': name, 'meta': {}, 'ingredients': [], 'steps': [], 'notes': []}
        current_section = None
        for line in lines[1:]:
            line = line.rstrip()
            m = re.match(r'\*\*([^:]+?)\s*:\*\*\s*(.+)', line)
            if m:
                key, val = m.groups()
                if '|' in val and '**' in val:
                    first_val = val.split(' | ')[0].strip()
                    recipe['meta'][key.strip()] = first_val
                    remaining = ' | '.join(val.split(' | ')[1:])
                    pairs = remaining.split(' | ')
                    for pair in pairs:
                        pair = pair.strip()
                        sub_m = re.match(r'\*\*([^:]+?)\s*:\*\*\s*(.+)', pair)
                        if sub_m:
                            sub_key, sub_val = sub_m.groups()
                            recipe['meta'][sub_key.strip()] = sub_val.strip()
                else:
                    recipe['meta'][key.strip()] = val.strip()
                continue
            if line.startswith('### '):
                section = line[4:].strip().lower()
                if 'ingrédient' in section or 'ingredient' in section:
                    current_section = 'ingredients'
                elif 'préparation' in section or 'preparation' in section:
                    current_section = 'steps'
                elif 'note' in section:
                    current_section = 'notes'
                continue
            if current_section and line.startswith('- '):
                item = line[2:].strip()
                if item:
                    recipe[current_section].append(item)
            elif current_section and re.match(r'^\d+\.\s', line):
                item = re.sub(r'^\d+\.\s*', '', line).strip()
                if item:
                    recipe['steps'].append(item)
        if recipe['name']:
            recipes.append(recipe)
    return recipes

def main():
    md = CONTENT.read_text(encoding='utf-8')
    recipes = parse_recipes(md)
    recipes_json = json.dumps(recipes, ensure_ascii=False)
    
    # Read JS file
    js_code = JS_FILE.read_text(encoding='utf-8')
    
    html = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mon Livre de Recettes</title>
  <style>''' + CSS + '''</style>
</head>
<body>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <button id="menu-btn" class="btn" aria-label="Menu" style="padding: 0.4rem;">''' + ICONS['menu'] + '''</button>
        <a href="#" class="logo">🍳 Recettes</a>
        <div class="search-box">
          ''' + ICONS['search'] + '''
          <input type="search" id="search-input" placeholder="Rechercher une recette…" aria-label="Rechercher">
        </div>
      </div>
      <div class="header-right">
        <a href="content/recettes.md" class="btn" target="_blank" rel="noopener">
          ''' + ICONS['source'] + '''
          <span class="btn-text">Source</span>
        </a>
      </div>
    </header>
    <aside class="sidebar" id="sidebar" role="navigation" aria-label="Catégories">
      <nav>
        <div class="sidebar-section">
          <div class="sidebar-title">Catégories</div>
          <ul class="category-list" id="category-list" role="listbox"></ul>
        </div>
      </nav>
    </aside>
    <main class="main" role="main">
      <div class="main-header">
        <h1 class="main-title" id="main-title">Toutes les recettes</h1>
        <p class="main-subtitle" id="main-subtitle">—</p>
      </div>
      <div class="recipes-grid" id="recipes-grid" role="list"></div>
      <div class="empty-state" id="empty-state" style="display: none;" aria-live="polite">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>
        <p>Aucune recette ne correspond à votre recherche.</p>
      </div>
    </main>
  </div>
  <script>
  window.RECIPES_DATA = ''' + recipes_json + ''';
  </script>
  <script>''' + js_code + '''</script>
</body>
</html>'''
    OUTPUT.write_text(html, encoding='utf-8')
    print("✅ Généré " + str(OUTPUT) + " (" + str(len(recipes)) + " recettes)")

if __name__ == '__main__':
    main()
