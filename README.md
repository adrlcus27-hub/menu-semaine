# 🍲 Menu de la semaine — Famille Lucas

Ce projet génère **chaque dimanche matin automatiquement** un menu complet
pour la semaine (14 repas : midi + soir, du lundi au dimanche), adapté aux
goûts et allergies de la famille, plus la liste de courses consolidée par
rayon. Le tout est publié sur une page web simple à consulter sur ton
téléphone.

La génération utilise l'API Claude (Anthropic) pour inventer des recettes
variées et cohérentes avec les contraintes familiales.

---

## Comment ça marche

```
Chaque dimanche à 8h (heure de Paris)
        │
        ▼
GitHub Actions réveille le script
        │
        ▼
Le script envoie à l'API Claude le profil familial
(allergies, préférences, budget, temps de préparation)
        │
        ▼
Claude génère 14 repas + liste de courses au format structuré
        │
        ▼
Génération d'une page HTML (menu + liste de courses)
        │
        ▼
Publication automatique sur GitHub Pages
```

---

## Installation (10 minutes, une seule fois)

Si tu as déjà installé le projet "veille-emploi" précédent, tu connais déjà
toutes ces étapes — c'est exactement le même principe, en plus simple (une
seule clé à configurer au lieu de deux).

### Étape 1 — Récupère une clé API Anthropic

1. Va sur **https://console.anthropic.com/**
2. Crée un compte si tu n'en as pas déjà un, ou connecte-toi
3. Va dans **"API Keys"** (dans les paramètres / settings)
4. Clique sur **"Create Key"**, donne-lui un nom (ex: `menu-semaine`)
5. **Copie la clé immédiatement** (elle commence par `sk-ant-...`) — elle ne
   sera plus jamais affichée en entier après

> 💡 Cette API est payante à l'usage, mais le coût est très faible pour cet
> usage (une génération par semaine) — généralement quelques centimes par
> semaine.

### Étape 2 — Crée le dépôt GitHub

1. Va sur **https://github.com/new**
2. Nom du dépôt : `menu-semaine` (ou ce que tu veux)
3. Visibilité : **Public** (nécessaire pour GitHub Pages gratuit, sauf si tu
   as un compte GitHub payant)
4. Ne coche aucune case d'initialisation
5. **"Create repository"**

Sur ton ordinateur, dans le Terminal :
```bash
cd chemin/vers/le/dossier/meal-planner
git init
git add .
git commit -m "Premier import du menu de la semaine"
git branch -M main
git remote add origin https://github.com/TON-PSEUDO/menu-semaine.git
git push -u origin main
```

### Étape 3 — Configure le secret GitHub

1. Sur la page de ton dépôt → **Settings** → **Secrets and variables** → **Actions**
2. **"New repository secret"**
3. Nom : `ANTHROPIC_API_KEY` → Valeur : ta clé `sk-ant-...`

### Étape 4 — Active GitHub Pages

1. **Settings** → **Pages**
2. Sous **"Source"**, choisis **"GitHub Actions"**

### Étape 5 — Premier test

1. Onglet **Actions** → workflow **"Menu de la semaine"**
2. **"Run workflow"** → confirme
3. Patiente 1-2 minutes (la génération du menu par l'IA prend un peu de temps)
4. Vérifie la coche verte ✅

### Étape 6 — Récupère ton lien

Dans **Settings** → **Pages**, ton URL apparaît en haut :
`https://ton-pseudo.github.io/menu-semaine/`

Mets-le en favori — c'est ton menu de la semaine, mis à jour chaque dimanche !

---

## Personnaliser les préférences familiales

Tout se règle dans **`config/famille.json`** :

```json
{
  "foyer": {
    "nombre_personnes": 4,
    "budget_hebdo": "équilibré (ni économique, ni premium)",
    "temps_preparation": "20-40 minutes en semaine",
    "proteines": "viande ou poisson à chaque repas"
  },
  "allergies_strictes": ["kiwi", "fruits à coque (...)"],
  "aliments_a_eviter": {
    "pere": ["abats"],
    "mere": ["poivrons", "raifort", "..."],
    "moi": ["céleri", "chou", "..."]
  }
}
```

- **`allergies_strictes`** : exclusion totale et systématique (sécurité)
- **`aliments_a_eviter`** : préférences/dégoûts, évités mais pas dramatique
  si ça apparaît occasionnellement
- **`preferences_generales`** : consignes de style ("cuisine variée", etc.)

Après modification :
```bash
git add config/famille.json
git commit -m "Met à jour les préférences familiales"
git push
```

Le prochain dimanche (ou le prochain lancement manuel) prendra en compte les
changements.

---

## Comment lire le menu

- **Onglet "Menu de la semaine"** : un bloc par jour, avec le repas du midi
  (bordure jaune moutarde) et du soir (bordure rouge tomate). Clique sur
  "Voir la recette" pour dérouler les ingrédients et les étapes.
- **Onglet "Liste de courses"** : regroupée par rayon, avec des cases à
  cocher pour suivre tes achats au fil des courses. ⚠️ Les coches ne se
  sauvegardent pas si tu fermes la page (c'est une page statique) — pratique
  pour une seule session de courses, pas pour suivre dans la durée.

---

## Limites à connaître

- Le menu est **généré par IA** : vérifie toujours que les allergies
  strictes sont bien respectées avant de cuisiner, en cas de doute sur un
  ingrédient. Le système est fiable mais une vérification reste prudente
  pour les allergies à enjeu sérieux.
- Les quantités de la liste de courses sont des **estimations raisonnables**,
  pas une pesée exacte — ajuste selon tes habitudes.
- Le menu est régénéré entièrement chaque dimanche ; si tu relances le
  workflow manuellement en semaine, ça génère un nouveau menu qui remplace
  celui en cours (utile si tu veux changer les plats de la semaine).

## Pour aller plus loin (non inclus, à la demande)

- Export de la liste de courses en PDF imprimable
- Ajustement automatique selon des plats déjà en stock
- Variante avec budget précis ou calories ciblées
- Sauvegarde persistante des coches de la liste de courses

Dis-moi si tu veux qu'on ajoute l'une de ces briques.
