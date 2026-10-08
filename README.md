# Kit de montage vidéo IA

Claude Code monte vos vidéos. Il coupe les blancs et les erreurs, choisit les bonnes prises,
alterne face cam et écran, zoome au bon moment et ajoute le motion design.
Il fabrique aussi les vidéos de marque : showreel, présentation, pub produit en 3 formats.
Tout tourne sur votre ordinateur. Les vidéos sont rendues en local avec HyperFrames.

C'est le kit présenté dans la vidéo « Opus 5.5 fait toute la com de votre entreprise ».

## Merci Nate Herk

Ce kit est construit sur le **[HyperFrames Student Kit](https://github.com/nateherkai/hyperframes-student-kit)
de Nate Herk**, sous licence MIT. Les skills de coupe, de storytelling, de showreel, de format court,
les 406 cartes de motion design et les modèles de scènes viennent de lui. Son travail est remarquable,
et il l'offre. Allez voir son dépôt et sa chaîne YouTube.

HyperFrames, le moteur de rendu, est un projet open source de HeyGen (licence Apache 2.0).

Son README d'origine est conservé ici : [README-NATE-HERK.md](README-NATE-HERK.md).

## Ce qu'on a ajouté

- **Le skill `youtube-long-form`** : le montage d'une vidéo YouTube longue tournée en deux fichiers
  (face cam + enregistrement d'écran). Synchro des deux sources (son contre son, avec correction
  de la dérive d'horloge entre les deux appareils, ou par compte à rebours si l'écran est muet),
  sélection des prises contre le script, une seule coupe des deux fichiers à l'image près,
  insertion de vidéos déjà rendues en plein écran, grammaire de mise en page et de zooms.
- **Les prompts de la vidéo**, dans [`prompts/`](prompts/README.md) : le showreel du hook, la vidéo
  de présentation d'une marque, la pub produit en 3 formats, le montage YouTube complet.
  En français, prêts à remplir.
- **Un gabarit de carte** « logo x métier » pour LinkedIn et les vignettes, dans
  [`templates/`](templates/carte-logo-x-metier/README.md).
- **La transcription via fal.ai** (même moteur ElevenLabs Scribe, sans compte ElevenLabs) :
  ajoutez `FAL_KEY` dans le `.env`.

## Ce qu'on a retiré

Pour garder un dépôt léger et propre :

- les vidéos d'exemple de Nate (99 Mo) et ses 12 projets pédagogiques (`video-projects/`) :
  ils sont sur [son dépôt](https://github.com/nateherkai/hyperframes-student-kit) ;
- les éléments de marque AI Automation Society (logo, charte), qui ne sont pas réutilisables ;
- le skill `short-form-video`, qui ne servait qu'à ces anciens projets. Pour les Reels et Shorts,
  utilisez `short-form-edit`.

## Ce qu'il vous faut

- **Claude Code** (un abonnement Claude). Codex fonctionne aussi.
- **Node.js 22 ou plus récent**, avec npm.
- **Git**.
- **FFmpeg** avec ffprobe, accessibles depuis le terminal.
- **Google Chrome** ou Chromium (pour le rendu).
- Pour le montage YouTube deux sources : **Python 3** et **[uv](https://docs.astral.sh/uv/)**
  (ou numpy installé).
- Optionnel, selon ce que vous faites : une clé fal.ai (transcription, images et vidéos générées),
  ElevenLabs, Kie.ai. Le premier test n'en demande aucune.

## Installation

Le plus simple : ouvrez Claude Code dans le dossier où vous voulez le kit, et collez ceci.

> Installe le kit de montage vidéo qui est ici : https://github.com/lenir923/kit-montage-video-ia
> Clone-le, vérifie que j'ai Node 22+, FFmpeg, ffprobe et Chrome (installe ce qui manque en me
> disant ce que tu fais), lance `npm ci`, `npm run setup` et `npm test`, puis rends la démo.
> Dis-moi à la fin ce qui marche et ce qu'il me reste à faire.

À la main, dans un terminal :

```sh
git clone https://github.com/lenir923/kit-montage-video-ia.git
cd kit-montage-video-ia
npm ci
npm run setup
npm test
```

`npm run setup` crée votre fichier `.env`. Remplissez seulement les clés des services que vous utilisez.
Le `.env` ne quitte jamais votre ordinateur : il est ignoré par Git.

## Premier test en 5 minutes

Ouvrez le dossier du kit dans Claude Code et collez :

> Crée un projet avec `npm run new-video -- premier-test`. Fais une animation de 8 secondes en
> 1920x1080 : le titre « Mon métier x IA » qui arrive lettre par lettre, puis trois mots clés
> qui tombent un par un, sur un fond sombre avec un léger grain. Vérifie avec le lint, rends-la
> en brouillon dans `video-projects/premier-test/renders/`, et montre-moi une image du milieu.

Aucune clé d'API, aucun coût. Si le MP4 sort, tout est en place.

Ensuite, essayez un vrai prompt de [`prompts/`](prompts/README.md).

## Ce qu'il y a dedans

| Dossier | Contenu |
| --- | --- |
| `.claude/skills/` | Les 15 skills (Claude Code). `.agents/skills/` en est le miroir pour Codex. |
| `prompts/` | Les 4 prompts de la vidéo, en français. |
| `templates/` | Le gabarit de carte « logo x métier ». |
| `style-library/` | 406 cartes de motion design en 2 styles, avec leur registre. |
| `style-templates/` | 2 modèles de scènes complètes. |
| `scripts/` | Transcription, nouveau projet, vérifications, synchro des skills. |
| `docs/` | La documentation de Nate (en anglais) : workflow, outils et clés, vérification. |
| `examples/` | Données de test synthétiques et projet de démarrage (sans vidéo). |

Vos projets vivent dans `video-projects/`, ignoré par Git : vos rushs ne partent nulle part.

Vous modifiez un skill ? Éditez-le dans `.claude/skills/`, puis lancez `npm run sync:skills`
pour mettre à jour le miroir Codex, et `npm run check` pour vérifier le kit.

## Licence

- Le kit de Nate Herk : licence MIT ([LICENSE](LICENSE)) et permission d'usage du pipeline
  ([licenses/PIPELINE-USE-PERMISSION.txt](licenses/PIPELINE-USE-PERMISSION.txt)).
- HyperFrames : Apache 2.0 ([licenses/HYPERFRAMES-LICENSE](licenses/HYPERFRAMES-LICENSE)).
- Ressources tierces : [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Nos ajouts (`youtube-long-form`, `prompts/`, `templates/`) : même licence MIT, par Léni Ragaigne.

Les logos et marques cités restent la propriété de leurs détenteurs.
