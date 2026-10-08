# Les prompts de la vidéo

Les 4 prompts utilisés dans la vidéo « Opus 5.5 fait toute la com de votre entreprise ».
Même structure, même niveau d'exigence. Seuls les noms, les liens et les chemins sont
devenus des champs à remplir, entre crochets : `[comme ceci]`.

| Fichier | Ce qu'il produit | Skill utilisé |
| --- | --- | --- |
| `01-showreel-hook.md` | Un showreel de motion design de 15 secondes, sans un mot | `motion-showreel` |
| `02-video-presentation-marque.md` | La vidéo de présentation d'une marque, à partir de son site et de sa charte | `website-to-hyperframes` |
| `03-pub-produit.md` | La pub d'un produit, en 3 formats (16:9, 9:16, 1:1) | aucun imposé |
| `04-montage-youtube-long.md` | Le montage complet d'une vidéo YouTube longue (face cam + écran) | `youtube-long-form` |

## Comment s'en servir

1. Ouvrez le dossier du kit dans Claude Code (Opus, effort « high » si vous l'avez).
2. Copiez le bloc de texte du prompt.
3. Remplacez chaque `[...]` par votre information. Supprimez les lignes qui ne vous concernent pas.
4. Collez, envoyez, laissez travailler.

Les clés d'API (génération d'images, transcription) vont dans le fichier `.env` à la racine du kit.
Jamais dans le prompt.
