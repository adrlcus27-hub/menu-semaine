#!/usr/bin/env python3
"""
Meal Planner - Famille Lucas
Génère chaque semaine un menu de 14 repas (midi + soir, 7 jours) + la liste
de courses associée, en respectant les allergies et préférences familiales,
via l'API Claude.

Usage:
    python3 generate_menu.py

Variable d'environnement requise:
    ANTHROPIC_API_KEY - Clé API Anthropic (https://console.anthropic.com)
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration & chemins
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "famille.json"
DATA_DIR = ROOT_DIR / "data"
HISTORY_PATH = DATA_DIR / "historique_menus.json"
DOCS_DIR = ROOT_DIR / "docs"
HTML_OUTPUT_PATH = DOCS_DIR / "index.html"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_VERSION = "2023-06-01"
REQUEST_TIMEOUT = 180  # la génération de 14 repas détaillés peut prendre du temps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("meal-planner")


# ---------------------------------------------------------------------------
# Chargement config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_history() -> list[dict]:
    """Charge les menus des semaines précédentes, pour éviter de répéter les mêmes plats."""
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Construction du prompt
# ---------------------------------------------------------------------------

def build_prompt(config: dict, recent_plats: list[str]) -> str:
    foyer = config["foyer"]
    allergies = config["allergies_strictes"]
    eviter = config["aliments_a_eviter"]
    preferences = config.get("preferences_generales", [])
    jours = config.get("jours_couverts", [])
    moments = config.get("repas_par_jour", ["midi", "soir"])

    eviter_lignes = []
    for personne, items in eviter.items():
        if personne.startswith("_"):
            continue
        if items:
            eviter_lignes.append(f"- {personne}: {', '.join(items)}")
    eviter_txt = "\n".join(eviter_lignes)

    recent_txt = ""
    if recent_plats:
        recent_txt = (
            "\n\nPlats déjà proposés les semaines précédentes (NE PAS LES REPROPOSER "
            "à l'identique cette semaine, varie les plaisirs) :\n- " + "\n- ".join(recent_plats)
        )

    nb_repas = len(jours) * len(moments)
    moments_txt = " et ".join(moments)

    prompt = f"""Tu es un assistant culinaire qui prépare le menu de la semaine pour une famille française.

CONTEXTE FAMILIAL :
- Nombre de personnes à table : {foyer['nombre_personnes']}
- Budget visé : {foyer['budget_hebdo']}
- Temps de préparation souhaité : {foyer['temps_preparation']}
- {foyer['proteines']}

⚠️ ALLERGIES STRICTES (exclusion totale, même en trace ou ingrédient secondaire) :
{', '.join(allergies)}

Aliments à éviter par préférence personnelle (pas une allergie, mais à ne pas utiliser comme ingrédient principal) :
{eviter_txt}

Préférences générales :
{chr(10).join('- ' + p for p in preferences)}
{recent_txt}

TÂCHE :
Génère un menu complet de {nb_repas} repas pour les 7 jours suivants : {', '.join(jours)}.
Chaque jour comporte un repas du {moments_txt} ({len(moments)} repas par jour).

Varie les types de plats entre le midi et le soir (par exemple, midi plus simple/rapide,
soir un peu plus élaboré, ou l'inverse selon ce qui est pratique) et entre les jours
(ne pas répéter la même protéine ou le même type de plat deux jours de suite).

Pour chaque repas, fournis :
- Le jour et le moment (midi ou soir)
- Le nom du plat
- Une courte description (1 phrase)
- La liste des ingrédients avec quantités précises, calculées pour {foyer['nombre_personnes']} personnes
- Le temps de préparation estimé en minutes
- 3-4 étapes de préparation résumées (pas une recette détaillée pas-à-pas, juste les grandes étapes)

Puis fournis une LISTE DE COURSES CONSOLIDÉE pour toute la semaine (les 14 repas), regroupée par rayon (ex: "Fruits & légumes", "Viandes & poissons", "Épicerie", "Produits laitiers", "Autres"), avec les quantités totales nécessaires en additionnant les besoins de tous les repas de la semaine.

IMPORTANT : réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte avant ou après, sans balises markdown ```json. Le JSON doit suivre exactement cette structure :

{{
  "menus": [
    {{
      "jour": "Lundi",
      "moment": "midi",
      "plat": "Nom du plat",
      "description": "Description courte",
      "temps_minutes": 30,
      "ingredients": [
        {{"nom": "ingrédient", "quantite": "quantité avec unité"}}
      ],
      "etapes": ["étape 1", "étape 2", "étape 3"]
    }}
  ],
  "liste_courses": [
    {{
      "rayon": "Fruits & légumes",
      "items": [
        {{"nom": "ingrédient", "quantite": "quantité totale"}}
      ]
    }}
  ]
}}
"""
    return prompt


# ---------------------------------------------------------------------------
# Appel API Claude
# ---------------------------------------------------------------------------

def call_claude(prompt: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY manquant. Configure-le en variable d'environnement (voir README).")
        sys.exit(1)

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": prompt}],
    }

    resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        log.error("Echec appel API Claude: %s - %s", resp.status_code, resp.text[:500])
        sys.exit(1)

    data = resp.json()
    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    full_text = "\n".join(text_blocks).strip()

    # Nettoyage défensif si jamais des balises markdown s'étaient glissées
    if full_text.startswith("```"):
        full_text = full_text.strip("`")
        if full_text.startswith("json"):
            full_text = full_text[4:].strip()

    try:
        return json.loads(full_text)
    except json.JSONDecodeError as e:
        log.error("Réponse de Claude non parsable en JSON: %s", e)
        log.error("Contenu reçu (tronqué): %s", full_text[:1000])
        sys.exit(1)


# ---------------------------------------------------------------------------
# Entrée principale
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=== Génération du menu de la semaine ===")
    config = load_config()
    history = load_history()

    # On récupère les plats des 3 dernières semaines pour éviter les répétitions
    recent_plats = []
    for semaine in history[:3]:
        for menu in semaine.get("menus", []):
            recent_plats.append(menu.get("plat", ""))

    prompt = build_prompt(config, recent_plats)
    log.info("Appel à l'API Claude...")
    menu_data = call_claude(prompt)

    n_menus = len(menu_data.get("menus", []))
    n_rayons = len(menu_data.get("liste_courses", []))
    log.info("%d menus générés, %d rayons dans la liste de courses.", n_menus, n_rayons)

    # Sauvegarde dans l'historique
    week_entry = {
        "semaine_du": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "menus": menu_data.get("menus", []),
        "liste_courses": menu_data.get("liste_courses", []),
    }
    history.insert(0, week_entry)
    history = history[:12]  # garde 12 semaines d'historique
    save_history(history)

    # Génération du HTML
    from generate_html import generate_dashboard
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    generate_dashboard(history, HTML_OUTPUT_PATH)
    log.info("Dashboard généré: %s", HTML_OUTPUT_PATH)

    log.info("=== Fin ===")


if __name__ == "__main__":
    main()
