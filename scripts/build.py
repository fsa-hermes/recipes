#!/usr/bin/env python3
"""
Générateur de site statique pour le livre de recettes — version Tech Dashboard.
"""
import os
import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content" / "recettes.md"
OUTPUT = ROOT / "index.html"

# ─── Icons ────────────────────────────────────────────────────────────
ICONS = {
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>',
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    'chevron_right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="9 18 15 12 9 6"></polyline></svg>',
    'x': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
    'salad': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
    'main': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>',
    'dessert': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
    'side': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M9 9h6v6H9z"></path></svg>',
    'drink': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M8 22h8"></path><path d="M12 11v11"></path><path d="M7 11a5 5 0 0 1 10 0v7"></path></svg>',
    'default': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="12" cy="12" r="10"></circle></svg>',
    'source': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    'ingredient': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>',
    'step': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M9 9h6v6H9z"></path></svg>',
    'note': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
}

CSS = r"""
:root {
  /* Cloudflare-inspired dark theme */
  --bg: #0e1116;
  --bg-elevated: #161b22;
  --card: #161b22;
  --card-hover: #1c2128;
  --border: #30363d;
  --border-hover: #388bfd;
  --fg: #e6edf3;
  --fg-muted: #8b949e;
  --fg-subtle: #6e7681;
  --accent: #388bfd;
  --accent-hover: #58a6ff;
  --accent-muted: rgba(56, 139, 253, 0.15);
  --danger: #f85149;
  --radius: 8px;
  --radius-sm: 6px;
  --sidebar-w: 180px;
  --header-h: 52px;
  --drawer-w: 420px;
  --shadow: 0 4px 12px rgba(0,0,0,0.4);
  --shadow-elevated: 0 8px 24px rgba(0,0,0,0.5);
  --transition: 120ms ease;
  --font-ui: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Inter, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; overflow: hidden; }

body {
  font-family: var(--font-ui);
  background: var(--bg);
  color: var(--fg);
  line-height: 1.5;
  font-size: 13px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app { display: grid; grid-template-columns: var(--sidebar-w) 1fr; grid-template-rows: var(--header-h) 1fr; height: 100vh; }

/* ─── Header ─── */
.header {
  grid-column: 1 / -1;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  height: var(--header-h);
  position: sticky; top: 0; z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.logo {
  font-size: 1rem; font-weight: 600; color: var(--accent);
  letter-spacing: -0.02em; text-decoration: none; display: flex; align-items: center; gap: 0.5rem;
}
.search-box { position: relative; width: 320px; flex-shrink: 0; }
.search-box input {
  width: 100%; padding: 0.4rem 0.75rem 0.4rem 2.25rem;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  font-size: 0.85rem; font-family: inherit;
  background: var(--bg); color: var(--fg);
  transition: border-color var(--transition), box-shadow var(--transition), background var(--transition);
}
.search-box input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-muted); background: var(--bg-elevated); }
.search-box input::placeholder { color: var(--fg-subtle); }
.search-box svg { position: absolute; left: 0.6rem; top: 50%; transform: translateY(-50%); stroke: var(--fg-subtle); pointer-events: none; }
.header-right { display: flex; align-items: center; gap: 0.5rem; }
.btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.4rem 0.75rem; border: 1px solid var(--border);
  border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all var(--transition); text-decoration: none;
  background: transparent; color: var(--fg-muted);
}
.btn:hover { background: var(--accent-muted); border-color: var(--accent); color: var(--accent); }
.btn-primary { background: var(--accent); border-color: var(--accent); color: #0d1117; }
.btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
.btn svg { width: 14px; height: 14px; flex-shrink: 0; }

/* ─── Sidebar ─── */
.sidebar {
  background: var(--bg-elevated);
  border-right: 1px solid var(--border);
  overflow-y: auto; padding: 0.75rem 0.5rem;
  position: sticky; top: var(--header-h); height: calc(100vh - var(--header-h));
}
.sidebar-section { margin-bottom: 1.5rem; }
.sidebar-title {
  font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--fg-subtle); margin-bottom: 0.5rem; font-weight: 600;
  padding: 0 0.5rem;
}
.category-list { list-style: none; }
.category-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.35rem 0.5rem; border-radius: var(--radius-sm);
  cursor: pointer; transition: background var(--transition), color var(--transition);
  color: var(--fg-muted); text-decoration: none; font-size: 0.85rem; font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.category-item:hover { background: var(--card); color: var(--fg); }
.category-item.active { background: var(--accent-muted); color: var(--accent); }
.category-icon { width: 14px; height: 14px; flex-shrink: 0; stroke: currentColor; opacity: 0.8; }
.category-count {
  margin-left: auto; font-size: 0.65rem; font-weight: 600;
  color: var(--fg-subtle); background: var(--bg); padding: 0.1rem 0.4rem; border-radius: 999px;
}
.category-item.active .category-count { background: var(--accent); color: #0d1117; }

/* ─── Main ─── */
.main { overflow-y: auto; padding: 1rem; background: var(--bg); }
.main-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem; }
.main-title { font-size: 1.1rem; font-weight: 600; color: var(--fg); }
.main-subtitle { color: var(--fg-subtle); font-size: 0.8rem; }

/* ─── Recipes Grid ─── */
.recipes-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.75rem;
}
.recipe-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow); transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  display: flex; flex-direction: column; min-height: 96px; cursor: pointer;
}
.recipe-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-elevated); border-color: var(--border-hover); }
.recipe-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.recipe-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; padding: 0.75rem; }
.recipe-name {
  font-size: 0.9rem; font-weight: 600; color: var(--fg); line-height: 1.3;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; min-width: 0;
}
.recipe-chevron { color: var(--fg-subtle); opacity: 0.5; transition: opacity var(--transition); flex-shrink: 0; }
.recipe-card:hover .recipe-chevron { opacity: 1; color: var(--accent); }

.recipe-meta { display: flex; flex-wrap: wrap; gap: 0.35rem; padding: 0 0.75rem 0.5rem; font-size: 0.7rem; }
.meta-item {
  display: inline-flex; align-items: center; gap: 0.25rem;
  color: var(--fg-muted); font-family: var(--font-mono);
}
.meta-item svg { width: 12px; height: 12px; opacity: 0.7; }

.tag {
  font-size: 0.6rem; font-weight: 600; padding: 0.15rem 0.45rem; border-radius: 4px;
  white-space: nowrap; border: 1px solid transparent; text-transform: uppercase; letter-spacing: 0.02em;
}
.tag-category { background: rgba(255, 184, 108, 0.15); color: #ffb86c; border-color: rgba(255, 184, 108, 0.3); }
.tag-difficulty-facile { background: rgba(63, 185, 80, 0.15); color: #3fb950; border-color: rgba(63, 185, 80, 0.3); }
.tag-difficulty-moyenne { background: rgba(255, 184, 108, 0.15); color: #ffb86c; border-color: rgba(255, 184, 108, 0.3); }
.tag-difficulty-difficile { background: rgba(248, 81, 73, 0.15); color: #f85149; border-color: rgba(248, 81, 73, 0.3); }
.tag-time { background: var(--bg); color: var(--fg-muted); border-color: var(--border); }
.tag-portions { background: rgba(56, 139, 253, 0.15); color: #58a6ff; border-color: rgba(56, 139, 253, 0.3); }
.tag-cost { background: rgba(255, 121, 198, 0.15); color: #ff79c6; border-color: rgba(255, 121, 198, 0.3); }

/* ─── Empty State ─── */
.empty-state {
  grid-column: 1 / -1; text-align: center; padding: 4rem 2rem; color: var(--fg-subtle);
}
.empty-state svg { width: 48px; height: 48px; margin-bottom: 1rem; opacity: 0.4; }

/* ─── Detail Drawer ─── */
.drawer-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  z-index: 200; opacity: 0; visibility: hidden; transition: opacity var(--transition), visibility var(--transition);
}
.drawer-overlay.open { opacity: 1; visibility: visible; }
.drawer {
  position: fixed; top: var(--header-h); right: 0; bottom: 0; width: var(--drawer-w);
  background: var(--bg-elevated); border-left: 1px solid var(--border);
  box-shadow: var(--shadow-elevated); z-index: 201;
  display: flex; flex-direction: column; transform: translateX(100%); transition: transform 200ms ease;
}
.drawer-overlay.open .drawer { transform: translateX(0); }
.drawer-header {
  display: flex; align-items: center; justify-content: space-between; padding: 1rem;
  border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.drawer-title { font-size: 1rem; font-weight: 600; color: var(--fg); }
.drawer-close { background: none; border: none; color: var(--fg-muted); cursor: pointer; padding: 0.25rem; border-radius: var(--radius-sm); transition: all var(--transition); }
.drawer-close:hover { background: var(--card); color: var(--fg); }
.drawer-body { flex: 1; overflow-y: auto; padding: 1rem; }
.drawer-section { margin-bottom: 1.5rem; }
.drawer-section-title {
  font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--fg-subtle); margin-bottom: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;
}
.drawer-section-title svg { color: var(--accent); opacity: 0.8; }
.detail-meta { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 1rem; }
.detail-list { list-style: none; font-size: 0.85rem; line-height: 1.7; }
.detail-list li { padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; align-items: flex-start; gap: 0.5rem; }
.detail-list li:last-child { border-bottom: none; }
.detail-list li::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); margin-top: 0.55rem; flex-shrink: 0; }
.steps-list { counter-reset: step; list-style: none; font-size: 0.85rem; line-height: 1.7; }
.steps-list li { padding: 0.5rem 0 0.5rem 2rem; border-bottom: 1px solid var(--border); position: relative; }
.steps-list li:last-child { border-bottom: none; }
.steps-list li::before { counter-increment: step; content: counter(step); position: absolute; left: 0; top: 0.5rem; width: 1.25rem; height: 1.25rem; background: var(--accent); color: #0d1117; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; font-family: var(--font-mono); }
.drawer-notes { font-size: 0.8rem; color: var(--fg-muted); line-height: 1.6; }
.drawer-notes ul { margin-left: 1rem; }
.drawer-notes li { margin-bottom: 0.3rem; }

/* ─── Responsive ─── */
@media (max-width: 1100px) {
  .app { grid-template-columns: 1fr; grid-template-rows: var(--header-h) auto 1fr; }
  .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); padding: 0.5rem; display: none; }
  .sidebar.open { display: block; }
  .main { padding: 0.75rem; }
  .recipes-grid { grid-template-columns: 1fr; }
  .search-box { width: 100%; max-width: none; }
  .header-right .btn-text { display: none; }
  .drawer { width: 100%; max-width: 100%; }
}
@media (max-width: 600px) {
  .header { padding: 0 0.75rem; }
  .recipe-header { padding: 0.6rem; }
  .recipe-meta { padding: 0 0.6rem 0.4rem; }
  .drawer-body { padding: 0.75rem; }
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--fg-subtle); }
"""

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
    js_code = JS_FILE.read_text(encoding='utf-8')
    html = '''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recettes — Tech Dashboard</title>
  <style>''' + CSS + '''</style>
</head>
<body>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <button id="menu-btn" class="btn" aria-label="Menu" style="padding: 0.3rem;">''' + ICONS['menu'] + '''</button>
        <a href="#" class="logo">''' + ICONS['main'] + ''' Recettes</a>
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
        <p>Aucune recette ne correspond.</p>
      </div>
    </main>
  </div>
  <div class="drawer-overlay" id="drawer-overlay" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
    <div class="drawer">
      <div class="drawer-header">
        <h2 class="drawer-title" id="drawer-title">Détail de la recette</h2>
        <button class="drawer-close" id="drawer-close" aria-label="Fermer">''' + ICONS['x'] + '''</button>
      </div>
      <div class="drawer-body" id="drawer-body"></div>
    </div>
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
