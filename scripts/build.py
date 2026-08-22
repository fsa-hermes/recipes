#!/usr/bin/env python3
"""
Générateur de site statique pour le livre de recettes.
Convertit content/recettes.md → index.html + style.css
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content" / "recettes.md"
OUTPUT = ROOT / "index.html"
ASSETS = ROOT / "assets"

CSS = """
:root {
  --bg: #faf9f6;
  --fg: #2d2d2d;
  --accent: #c0392b;
  --accent-light: #e74c3c;
  --card: #ffffff;
  --border: #e0ddd8;
  --muted: #6b6b6b;
  --shadow: 0 2px 8px rgba(0,0,0,0.06);
  --radius: 12px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.6;
  min-height: 100vh;
}

header {
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 2rem 1.5rem;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}

header h1 {
  font-size: clamp(1.8rem, 5vw, 2.5rem);
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.02em;
}

header p { color: var(--muted); margin-top: 0.5rem; }

main { max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem; }

.recipe {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
  transition: transform 0.2s, box-shadow 0.2s;
}

.recipe:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }

.recipe-header { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; align-items: baseline; }

.recipe h2 { font-size: 1.4rem; font-weight: 600; color: var(--fg); flex: 1; min-width: 200px; }

.meta { display: flex; flex-wrap: wrap; gap: 0.5rem; font-size: 0.8rem; color: var(--muted); }

.badge {
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}

.badge-category { background: #fff3e0; border-color: #ffe0b2; color: #e65100; }
.badge-difficulty-facile { background: #e8f5e9; border-color: #c8e6c9; color: #2e7d32; }
.badge-difficulty-moyenne { background: #fff3e0; border-color: #ffe0b2; color: #e65100; }
.badge-difficulty-difficile { background: #ffebee; border-color: #ffcdd2; color: #c62828; }

.section { margin-top: 1.25rem; }

.section-title {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.4rem;
  margin-bottom: 0.75rem;
}

.ingredients { columns: 2; column-gap: 2rem; }
.ingredients li { break-inside: avoid; margin-bottom: 0.3rem; }

.steps { counter-reset: step; }
.steps li {
  list-style: none;
  position: relative;
  padding-left: 2rem;
  margin-bottom: 0.75rem;
}
.steps li::before {
  counter-increment: step;
  content: counter(step);
  position: absolute;
  left: 0;
  top: 0;
  width: 1.5rem;
  height: 1.5rem;
  background: var(--accent);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.notes {
  background: #fdfbf7;
  border-left: 3px solid var(--accent);
  padding: 1rem;
  border-radius: 0 var(--radius) var(--radius) 0;
  font-size: 0.9rem;
}
.notes ul { margin-left: 1.2rem; }
.notes li { margin-bottom: 0.3rem; }

hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}

@media (max-width: 600px) {
  .ingredients { columns: 1; }
  .recipe { padding: 1rem; }
}
"""

def parse_recipes(md_text):
    """Parse le markdown en liste de dicts recettes."""
    # Split par "### " (niveau 3 = nom de recette)
    # Le fichier commence par un intro, puis les recettes
    parts = re.split(r'\n###\s+', md_text)
    recipes = []
    
    for part in parts[1:]:  # skip intro
        lines = part.strip().split('\n')
        if not lines:
            continue
            
        name = lines[0].strip()
        recipe = {'name': name, 'meta': {}, 'ingredients': [], 'steps': [], 'notes': []}
        
        current_section = None
        for line in lines[1:]:
            line = line.rstrip()
            
            # Métadonnées : **Clé :** Valeur
            m = re.match(r'\*\*([^*]+)\s*:\*\*\s*(.+)', line)
            if m:
                key, val = m.groups()
                recipe['meta'][key.strip()] = val.strip()
                continue
            
            # Sections
            if line.startswith('### '):
                section = line[4:].strip().lower()
                if 'ingrédient' in section:
                    current_section = 'ingredients'
                elif 'préparation' in section or 'preparation' in section:
                    current_section = 'steps'
                elif 'note' in section:
                    current_section = 'notes'
                continue
            
            # Contenu des sections
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

def render_recipe(r):
    meta_html = ''
    if r['meta']:
        badges = []
        cat = r['meta'].get('Catégorie', '')
        if cat:
            badges.append(f'<span class="badge badge-category">{cat}</span>')
        diff = r['meta'].get('Difficulté', '').lower()
        if diff:
            badges.append(f'<span class="badge badge-difficulty-{diff}">{diff.capitalize()}</span>')
        for k, v in r['meta'].items():
            if k not in ['Catégorie', 'Difficulté']:
                badges.append(f'<span class="badge">{k}: {v}</span>')
        meta_html = f'<div class="meta">{"".join(badges)}</div>'
    
    ing_html = ''
    if r['ingredients']:
        items = ''.join(f'<li>{i}</li>' for i in r['ingredients'])
        ing_html = f'<div class="section"><div class="section-title">Ingrédients</div><ul class="ingredients">{items}</ul></div>'
    
    steps_html = ''
    if r['steps']:
        items = ''.join(f'<li>{s}</li>' for s in r['steps'])
        steps_html = f'<div class="section"><div class="section-title">Préparation</div><ol class="steps">{items}</ol></div>'
    
    notes_html = ''
    if r['notes']:
        items = ''.join(f'<li>{n}</li>' for n in r['notes'])
        notes_html = f'<div class="section notes"><div class="section-title">Notes</div><ul>{items}</ul></div>'
    
    return f'''
<article class="recipe">
  <div class="recipe-header">
    <h2>{r['name']}</h2>
    {meta_html}
  </div>
  {ing_html}
  {steps_html}
  {notes_html}
</article>'''

def main():
    md = CONTENT.read_text(encoding='utf-8')
    recipes = parse_recipes(md)
    
    recipes_html = ''.join(render_recipe(r) for r in recipes)
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mon Livre de Recettes</title>
  <style>{CSS}</style>
</head>
<body>
  <header>
    <h1>🍳 Mon Livre de Recettes</h1>
    <p>{len(recipes)} recettes — fait main, à jour</p>
  </header>
  <main>
    {recipes_html}
  </main>
  <footer>
    Généré automatiquement depuis <code>content/recettes.md</code> • 
    <a href="content/recettes.md" style="color:var(--accent);">Voir la source</a>
  </footer>
</body>
</html>'''
    
    OUTPUT.write_text(html, encoding='utf-8')
    print(f"✅ Généré {OUTPUT} ({len(recipes)} recettes)")

if __name__ == '__main__':
    main()