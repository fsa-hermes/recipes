// State
const state = {
  recipes: [],
  filtered: [],
  activeCategory: 'all',
  searchQuery: ''
};

// DOM
const els = {
  searchInput: document.getElementById('search-input'),
  categoryList: document.getElementById('category-list'),
  recipesGrid: document.getElementById('recipes-grid'),
  mainTitle: document.getElementById('main-title'),
  mainSubtitle: document.getElementById('main-subtitle'),
  emptyState: document.getElementById('empty-state'),
  sidebar: document.getElementById('sidebar'),
  menuBtn: document.getElementById('menu-btn')
};

// Icons
const ICONS = {
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
  salad: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
  main: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>',
  dessert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.52 2 12 2z"></path><path d="M12 6v6l4 2"></path></svg>',
  side: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M9 9h6v6H9z"></path></svg>',
  drink: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 22h8"></path><path d="M12 11v11"></path><path d="M7 11a5 5 0 0 1 10 0v7"></path></svg>',
  default: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>'
};

function getCategoryIcon(cat) {
  const key = cat.toLowerCase().replace('é', 'e').replace('è', 'e');
  return ICONS[key] || ICONS.default;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, '"')
    .replace(/'/g, "'");
}

function renderCategories(categories) {
  const allCount = state.recipes.length;
  const activeCount = state.filtered.length;
  let html = '<li class="category-item ' + (state.activeCategory === 'all' ? 'active' : '') + '" data-category="all">' + ICONS.menu + ' <span>Toutes</span><span class="category-count">' + activeCount + ' / ' + allCount + '</span></li>';
  categories.forEach(function(cat) {
    const count = state.recipes.filter(function(r) { return r.meta["Catégorie"] === cat; }).length;
    const filteredCount = state.filtered.filter(function(r) { return r.meta["Catégorie"] === cat; }).length;
    const isActive = state.activeCategory === cat;
    html += '<li class="category-item ' + (isActive ? 'active' : '') + '" data-category="' + escapeHtml(cat) + '">' + getCategoryIcon(cat) + ' <span>' + escapeHtml(cat) + '</span><span class="category-count">' + filteredCount + ' / ' + count + '</span></li>';
  });
  els.categoryList.innerHTML = html;
  document.querySelectorAll('.category-item').forEach(function(item) {
    item.addEventListener('click', function() {
      state.activeCategory = item.dataset.category;
      applyFilters();
      closeSidebar();
    });
  });
}

function renderRecipes() {
  console.log('[Recipes] Rendering', state.filtered.length, 'recipes');
  if (state.filtered.length === 0) {
    els.recipesGrid.style.display = 'none';
    els.emptyState.style.display = 'block';
    return;
  }
  els.recipesGrid.style.display = 'grid';
  els.emptyState.style.display = 'none';
  els.recipesGrid.innerHTML = state.filtered.map(function(recipe, idx) {
    return '<article class="recipe-card" style="animation-delay: ' + (idx * 30) + 'ms" data-category="' + escapeHtml(recipe.meta['Catégorie'] || '') + '"><div class="recipe-header"><h3 class="recipe-name">' + escapeHtml(recipe.name) + '</h3></div><div class="recipe-meta">' + renderTags(recipe.meta) + '</div><div class="recipe-divider"></div><div class="recipe-body">' + (recipe.ingredients.length ? '<div class="recipe-section"><div class="recipe-section-title">Ingrédients</div><ul class="ingredients-list">' + recipe.ingredients.map(function(i) { return '<li>' + escapeHtml(i) + '</li>'; }).join('') + '</ul></div>' : '') + (recipe.steps.length ? '<div class="recipe-section"><div class="recipe-section-title">Préparation</div><ol class="steps-list">' + recipe.steps.map(function(s) { return '<li>' + escapeHtml(s) + '</li>'; }).join('') + '</ol></div>' : '') + (recipe.notes.length ? '<details class="recipe-notes"><summary>Notes</summary><ul>' + recipe.notes.map(function(n) { return '<li>' + escapeHtml(n) + '</li>'; }).join('') + '</ul></details>' : '') + '</div></article>';
  }).join('');
  console.log('[Recipes] Done rendering');
}

function renderTags(meta) {
  var tags = [];
  if (meta['Catégorie']) tags.push('<span class="tag tag-category">' + escapeHtml(meta['Catégorie']) + '</span>');
  if (meta['Difficulté']) tags.push('<span class="tag tag-difficulty-' + meta['Difficulté'].toLowerCase() + '">' + escapeHtml(meta['Difficulté']) + '</span>');
  if (meta['Temps']) tags.push('<span class="tag tag-time">' + escapeHtml(meta['Temps']) + '</span>');
  if (meta['Portions']) tags.push('<span class="tag tag-portions">' + escapeHtml(meta['Portions']) + '</span>');
  if (meta['Coût']) tags.push('<span class="tag tag-cost">' + escapeHtml(meta['Coût']) + '</span>');
  return tags.join('');
}

function updateHeader() {
  var catName = state.activeCategory === 'all' ? 'Toutes les recettes' : state.activeCategory;
  var count = state.filtered.length;
  els.mainTitle.textContent = catName;
  els.mainSubtitle.textContent = count + ' recette' + (count > 1 ? 's' : '') + (state.searchQuery ? ' • filtrée' + state.searchQuery : '');
}

function applyFilters() {
  var result = state.recipes.slice();
  if (state.activeCategory !== 'all') {
    result = result.filter(function(r) { return r.meta['Catégorie'] === state.activeCategory; });
  }
  if (state.searchQuery) {
    var q = state.searchQuery.toLowerCase();
    result = result.filter(function(r) {
      return r.name.toLowerCase().includes(q) || r.ingredients.some(function(i) { return i.toLowerCase().includes(q); }) || r.steps.some(function(s) { return s.toLowerCase().includes(q); }) || r.notes.some(function(n) { return n.toLowerCase().includes(q); }) || JSON.stringify(r.meta).toLowerCase().includes(q);
    });
  }
  state.filtered = result;
  renderCategories(getCategories());
  renderRecipes();
  updateHeader();
}

function getCategories() {
  var cats = new Set();
  state.recipes.forEach(function(r) { if (r.meta['Catégorie']) cats.add(r.meta['Catégorie']); });
  return Array.from(cats).sort();
}

function closeSidebar() {
  if (window.innerWidth <= 900) {
    els.sidebar.classList.remove('open');
  }
}

function init() {
  console.log('[Init] Starting...');
  state.recipes = window.RECIPES_DATA || [];
  console.log('[Init] Loaded', state.recipes.length, 'recipes from RECIPES_DATA');
  state.filtered = state.recipes.slice();
  renderCategories(getCategories());
  renderRecipes();
  updateHeader();
  var searchTimeout;
  els.searchInput.addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
      state.searchQuery = e.target.value.trim();
      applyFilters();
    }, 120);
  });
  els.menuBtn.addEventListener('click', function() {
    els.sidebar.classList.toggle('open');
  });
  document.addEventListener('click', function(e) {
    if (window.innerWidth <= 900 && !els.sidebar.contains(e.target) && !els.menuBtn.contains(e.target) && els.sidebar.classList.contains('open')) {
      els.sidebar.classList.remove('open');
    }
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSidebar();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === '/' && document.activeElement !== els.searchInput) {
      e.preventDefault();
      els.searchInput.focus();
    }
  });
  console.log('[Init] Complete');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}