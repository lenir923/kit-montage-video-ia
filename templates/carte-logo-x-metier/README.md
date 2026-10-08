# Gabarit « logo x métier »

Une carte simple qui marche très bien sur LinkedIn et en vignette : fond blanc cassé,
le logo d'un outil en relief, un « x », le métier ou le secteur en gros. Rien d'autre.

- `carte.html` : 1600x900 (16:9). `carte-carre.html` : 1200x1200 (carré).
- Texte à changer : la div `.right` (deux lignes, séparées par `<br>`).
- Logo : remplacez `claude.svg` par l'icône de votre outil. Les icônes de marques
  sont sur [simpleicons.org](https://simpleicons.org) (en blanc :
  `https://cdn.simpleicons.org/<marque>/ffffff`). Changez aussi le nom sous le logo
  (div `.name`) et le dégradé de la tuile (`.tile`) aux couleurs de l'outil.
- Les logos restent la propriété de leurs marques : utilisez-les pour parler de l'outil,
  pas pour laisser croire à un partenariat.

## Rendu en PNG

Le plus simple : demandez à Claude Code « rends `templates/carte-logo-x-metier/carte.html` en PNG ».
À la main, avec Chrome en mode headless (environ 2 secondes) :

```sh
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --no-first-run --virtual-time-budget=8000 --window-size=1600,900 \
  --screenshot="carte.png" "file://$PWD/carte.html"
```

Sous Windows ou Linux, même commande avec le chemin de votre Chrome (`chrome`, `google-chrome`).
Pour la carte carrée : `--window-size=1200,1200`.

Sur macOS, Chrome headless écrit parfois le fichier sans rendre la main : attendez que
le PNG soit écrit, puis fermez le processus.
