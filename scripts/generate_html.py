#!/usr/bin/env python3
"""
Génère le dashboard HTML du menu de la semaine + liste de courses.
Design: carnet de recettes familial chaleureux (marché, épicerie de quartier).
"""

import html
from datetime import datetime
from pathlib import Path

JOURS_ORDRE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def format_date_fr(dt: datetime) -> str:
    return f"{dt.day} {MOIS_FR[dt.month - 1]} {dt.year}"


def meal_card_html(menu: dict) -> str:
    jour = html.escape(menu.get("jour", ""))
    moment = menu.get("moment", "soir")
    moment_label = "Midi" if moment == "midi" else "Soir"
    plat = html.escape(menu.get("plat", "Plat à définir"))
    description = html.escape(menu.get("description", ""))
    temps = menu.get("temps_minutes", "?")
    ingredients = menu.get("ingredients", [])
    etapes = menu.get("etapes", [])

    ingredients_html = "".join(
        f'<li>{html.escape(ing.get("quantite", ""))} {html.escape(ing.get("nom", ""))}</li>'
        for ing in ingredients
    )
    etapes_html = "".join(
        f'<li>{html.escape(etape)}</li>' for etape in etapes
    )

    moment_class = "midi" if moment == "midi" else "soir"

    return f"""
    <article class="meal-card meal-card--{moment_class}">
      <div class="meal-card__header">
        <span class="meal-card__moment">{moment_label}</span>
        <span class="meal-card__time">⏱ {temps} min</span>
      </div>
      <h3 class="meal-card__title">{plat}</h3>
      <p class="meal-card__desc">{description}</p>
      <details class="meal-card__details">
        <summary>Voir la recette</summary>
        <div class="meal-card__recipe">
          <h4>Ingrédients</h4>
          <ul class="meal-card__ingredients">{ingredients_html}</ul>
          <h4>Étapes</h4>
          <ol class="meal-card__steps">{etapes_html}</ol>
        </div>
      </details>
    </article>"""


def day_section_html(jour: str, menus_du_jour: list[dict]) -> str:
    cards = "".join(meal_card_html(m) for m in menus_du_jour)
    return f"""
    <section class="day-block">
      <h2 class="day-block__title">{html.escape(jour)}</h2>
      <div class="day-block__meals">{cards}</div>
    </section>"""


def shopping_list_html(liste_courses: list[dict]) -> str:
    rayons_html = ""
    for rayon in liste_courses:
        nom_rayon = html.escape(rayon.get("rayon", ""))
        items = rayon.get("items", [])
        items_html = "".join(
            f'''<li class="shop-item">
                  <label>
                    <input type="checkbox" class="shop-item__check">
                    <span class="shop-item__qty">{html.escape(item.get("quantite", ""))}</span>
                    <span class="shop-item__name">{html.escape(item.get("nom", ""))}</span>
                  </label>
                </li>'''
            for item in items
        )
        rayons_html += f"""
        <div class="shop-rayon">
          <h3 class="shop-rayon__title">{nom_rayon}</h3>
          <ul class="shop-rayon__items">{items_html}</ul>
        </div>"""
    return rayons_html


def generate_dashboard(history: list[dict], output_path: Path) -> None:
    if not history:
        week = {"semaine_du": datetime.now().strftime("%Y-%m-%d"), "menus": [], "liste_courses": []}
    else:
        week = history[0]

    try:
        semaine_dt = datetime.strptime(week["semaine_du"], "%Y-%m-%d")
        semaine_label = f"Semaine du {format_date_fr(semaine_dt)}"
    except (ValueError, KeyError):
        semaine_label = "Cette semaine"

    menus = week.get("menus", [])
    liste_courses = week.get("liste_courses", [])

    # Regroupement des menus par jour, dans l'ordre Lundi -> Dimanche
    menus_par_jour: dict[str, list[dict]] = {}
    for m in menus:
        jour = m.get("jour", "")
        menus_par_jour.setdefault(jour, []).append(m)
    for jour_menus in menus_par_jour.values():
        jour_menus.sort(key=lambda m: 0 if m.get("moment") == "midi" else 1)

    jours_presents = [j for j in JOURS_ORDRE if j in menus_par_jour]
    jours_html = "".join(
        day_section_html(j, menus_par_jour[j]) for j in jours_presents
    )

    n_repas = len(menus)
    n_items_courses = sum(len(r.get("items", [])) for r in liste_courses)

    shopping_html = shopping_list_html(liste_courses)

    now_label = datetime.now().strftime("%d/%m/%Y à %Hh%M")

    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Le menu de la semaine — Famille Lucas</title>
<style>
  :root {{
    --kraft: #f3ead9;
    --kraft-deep: #e8dcc4;
    --ink: #2e2419;
    --ink-soft: #6b5d49;
    --sauge: #6b7a52;
    --sauge-deep: #4f5c3a;
    --moutarde: #d39a2e;
    --tomate: #c0533b;
    --card: #fffaf0;
    --line: #d9cba8;
    --serif: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
    --hand: Georgia, 'Iowan Old Style', serif;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--kraft);
    background-image:
      radial-gradient(circle at 20% 10%, rgba(107,122,82,0.05), transparent 40%),
      radial-gradient(circle at 90% 80%, rgba(192,83,59,0.04), transparent 40%);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }}

  .wrap {{
    max-width: 1080px;
    margin: 0 auto;
    padding: 0 24px 100px;
  }}

  /* ---------- HEADER ---------- */
  header.hero {{
    padding: 56px 0 40px;
    text-align: center;
  }}

  .hero__eyebrow {{
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--sauge-deep);
    font-weight: 700;
    margin-bottom: 10px;
  }}

  h1.hero__title {{
    font-family: var(--serif);
    font-size: clamp(36px, 6vw, 56px);
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 1.1;
    color: var(--ink);
    margin-bottom: 10px;
  }}

  .hero__title em {{
    font-style: italic;
    color: var(--tomate);
  }}

  .hero__sub {{
    color: var(--ink-soft);
    font-size: 16px;
    margin-bottom: 22px;
  }}

  .hero__stats {{
    display: inline-flex;
    gap: 28px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 100px;
    padding: 10px 28px;
    font-size: 14px;
  }}

  .hero__stat strong {{
    color: var(--sauge-deep);
    font-weight: 700;
  }}

  .hero__updated {{
    font-size: 12px;
    color: var(--ink-soft);
    margin-top: 18px;
    opacity: 0.8;
  }}

  /* ---------- NAV TABS ---------- */
  .tabs {{
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 40px;
    flex-wrap: wrap;
  }}

  .tab {{
    font-family: var(--serif);
    font-size: 15px;
    font-weight: 600;
    padding: 10px 22px;
    border-radius: 100px;
    border: 1px solid var(--line);
    background: var(--card);
    color: var(--ink-soft);
    cursor: pointer;
  }}

  .tab.active {{
    background: var(--sauge-deep);
    color: var(--kraft);
    border-color: var(--sauge-deep);
  }}

  /* ---------- DAY BLOCKS (Menu) ---------- */
  .day-block {{
    margin-bottom: 36px;
  }}

  .day-block__title {{
    font-family: var(--serif);
    font-size: 22px;
    font-weight: 600;
    color: var(--sauge-deep);
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--sauge);
    display: inline-block;
  }}

  .day-block__meals {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 18px;
  }}

  .meal-card {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px;
    position: relative;
    box-shadow: 0 2px 6px rgba(46, 36, 25, 0.04);
  }}

  .meal-card--midi {{ border-top: 4px solid var(--moutarde); }}
  .meal-card--soir {{ border-top: 4px solid var(--tomate); }}

  .meal-card__header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}

  .meal-card__moment {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-soft);
  }}

  .meal-card__time {{
    font-size: 12px;
    color: var(--ink-soft);
  }}

  .meal-card__title {{
    font-family: var(--serif);
    font-size: 19px;
    font-weight: 600;
    margin-bottom: 6px;
    line-height: 1.3;
  }}

  .meal-card__desc {{
    font-size: 13.5px;
    color: var(--ink-soft);
    margin-bottom: 12px;
  }}

  .meal-card__details summary {{
    font-size: 13px;
    font-weight: 600;
    color: var(--sauge-deep);
    cursor: pointer;
    list-style: none;
  }}

  .meal-card__details summary::-webkit-details-marker {{ display: none; }}
  .meal-card__details summary::before {{ content: "🍴 "; }}

  .meal-card__recipe {{
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px dashed var(--line);
  }}

  .meal-card__recipe h4 {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink-soft);
    margin: 10px 0 6px;
  }}

  .meal-card__ingredients,
  .meal-card__steps {{
    font-size: 13.5px;
    padding-left: 20px;
  }}

  .meal-card__ingredients li,
  .meal-card__steps li {{
    margin-bottom: 4px;
  }}

  /* ---------- SHOPPING LIST ---------- */
  .shop-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
  }}

  .shop-rayon {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px;
  }}

  .shop-rayon__title {{
    font-family: var(--serif);
    font-size: 17px;
    font-weight: 600;
    color: var(--sauge-deep);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--line);
  }}

  .shop-rayon__items {{
    list-style: none;
  }}

  .shop-item {{
    margin-bottom: 8px;
  }}

  .shop-item label {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
  }}

  .shop-item__check {{
    width: 15px;
    height: 15px;
    accent-color: var(--sauge-deep);
    flex-shrink: 0;
  }}

  .shop-item__qty {{
    color: var(--ink-soft);
    font-size: 12.5px;
    min-width: 70px;
  }}

  .shop-item__name {{
    color: var(--ink);
  }}

  .shop-item input:checked ~ .shop-item__name,
  .shop-item input:checked + .shop-item__qty {{
    text-decoration: line-through;
    opacity: 0.45;
  }}

  /* Note: la coche checkbox ne persiste pas après rafraîchissement (page statique) */
  .shop-note {{
    text-align: center;
    font-size: 12px;
    color: var(--ink-soft);
    margin-top: 24px;
    opacity: 0.8;
  }}

  section.panel {{ display: none; }}
  section.panel.active {{ display: block; }}

  footer.page-footer {{
    text-align: center;
    color: var(--ink-soft);
    font-size: 12px;
    padding-top: 40px;
    opacity: 0.8;
  }}

  @media (max-width: 600px) {{
    header.hero {{ padding: 40px 0 28px; }}
    .hero__stats {{ flex-direction: column; gap: 6px; padding: 14px 24px; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="hero__eyebrow">Famille Lucas</div>
      <h1 class="hero__title">Le menu de la <em>semaine</em></h1>
      <p class="hero__sub">{semaine_label} — généré automatiquement selon les goûts et allergies de la famille</p>
      <div class="hero__stats">
        <span class="hero__stat"><strong>{n_repas}</strong> repas planifiés</span>
        <span class="hero__stat"><strong>{n_items_courses}</strong> articles à acheter</span>
      </div>
      <p class="hero__updated">Dernière génération : {now_label}</p>
    </header>

    <div class="tabs">
      <button class="tab active" onclick="showPanel('menu')" id="tab-menu">📅 Menu de la semaine</button>
      <button class="tab" onclick="showPanel('courses')" id="tab-courses">🛒 Liste de courses</button>
    </div>

    <section class="panel active" id="panel-menu">
      {jours_html}
    </section>

    <section class="panel" id="panel-courses">
      <div class="shop-grid">
        {shopping_html}
      </div>
      <p class="shop-note">Coche les articles au fur et à mesure — la coche ne se sauvegarde pas si tu fermes la page.</p>
    </section>

    <footer class="page-footer">
      Généré automatiquement chaque semaine · Respecte les allergies et préférences enregistrées · Aucune donnée personnelle stockée en ligne
    </footer>
  </div>

  <script>
    function showPanel(name) {{
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('panel-' + name).classList.add('active');
      document.getElementById('tab-' + name).classList.add('active');
    }}
  </script>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_doc, encoding="utf-8")


if __name__ == "__main__":
    # Test local avec données factices
    sample_history = [{
        "semaine_du": datetime.now().strftime("%Y-%m-%d"),
        "menus": [
            {
                "jour": "Lundi", "moment": "midi", "plat": "Poulet rôti aux herbes et pommes de terre",
                "description": "Un classique réconfortant et facile à préparer.",
                "temps_minutes": 35,
                "ingredients": [
                    {"nom": "blancs de poulet", "quantite": "600 g"},
                    {"nom": "pommes de terre", "quantite": "800 g"},
                    {"nom": "thym", "quantite": "1 cuillère à café"},
                ],
                "etapes": ["Préchauffer le four à 200°C", "Disposer le poulet et les pommes de terre", "Cuire 30 minutes"],
            },
            {
                "jour": "Lundi", "moment": "soir", "plat": "Saumon à l'unilatéral, riz et brocolis",
                "description": "Léger et riche en oméga-3, parfait pour le soir.",
                "temps_minutes": 25,
                "ingredients": [
                    {"nom": "pavés de saumon", "quantite": "4"},
                    {"nom": "riz basmati", "quantite": "300 g"},
                    {"nom": "brocolis", "quantite": "400 g"},
                ],
                "etapes": ["Cuire le riz", "Poêler le saumon côté peau", "Cuire les brocolis à la vapeur"],
            },
        ],
        "liste_courses": [
            {
                "rayon": "Viandes & poissons",
                "items": [
                    {"nom": "blancs de poulet", "quantite": "600 g"},
                    {"nom": "pavés de saumon", "quantite": "4"},
                ],
            },
            {
                "rayon": "Fruits & légumes",
                "items": [
                    {"nom": "pommes de terre", "quantite": "800 g"},
                    {"nom": "brocolis", "quantite": "400 g"},
                ],
            },
        ],
    }]
    generate_dashboard(sample_history, Path("docs/index.html"))
    print("OK - test généré dans docs/index.html")
