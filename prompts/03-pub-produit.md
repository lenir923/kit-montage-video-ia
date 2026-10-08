# Prompt : la pub d'un produit, en 3 formats

> À coller dans Claude Code, dossier ouvert = la racine du kit, effort « high ».
> Les plans illustratifs sont générés avec fal.ai : mettez votre clé `FAL_KEY` dans le `.env` du kit.
> Choisissez un produit qui a une preuve forte (un prix, une note, un chiffre). C'est le cœur de la pub.

```text
Fais-moi une pub de 15 secondes (20 maximum) pour un produit de cette marque : [nom du produit] de [nom de la marque].
Full motion design. Lâche-toi complètement.
Elle doit être postable telle quelle sur les réseaux.

Tout est sur leur site :
- la page du produit : [URL de la page du produit]
- la marque : [URL du site de la marque]
[La preuve forte du produit, par exemple : Ce produit a été élu meilleur produit de sa catégorie en 2025.] Vérifie-le sur le site, et fais-en le cœur de la pub.

Leur charte graphique, à respecter à la lettre (logo, couleurs, typos, règles d'usage) :
"[chemin de la charte graphique, PDF]"
"[chemin d'un deuxième document de marque si vous en avez un]"

Les images : pars des vraies photos du produit et de la marque sur le site. Utilise-les comme images de référence avec fal.ai (clé FAL_KEY dans le .env) pour créer les plans d'illustration dont tu as besoin : [les plans qui donnent envie pour ce produit, par exemple pour un produit alimentaire : gros plans macro, ingrédients en suspension, chutes au ralenti, plans vidéo animés à partir d'une image]. Le produit doit rester fidèle à la réalité : même forme, même couleur, même emballage. Jamais de personne générée.

Ce que je veux ressentir en la regardant : "Il me le faut. Tout de suite." [La sensation propre au produit, par exemple : de la gourmandise pure, du croquant qu'on entend presque], et la fierté d'un produit primé. Un peu de FOMO.

Les règles :
- Court et chargé plutôt que long et vide. Il se passe toujours quelque chose. Pas une seule seconde morte.
- Tout se comprend par l'image. Le minimum de texte : le nom du produit, la preuve, le logo. Pas de phrases.
- Ce n'est pas la vidéo de présentation de la marque : c'est la pub d'UN produit. Tout tourne autour de lui.
- N'utilise pas le skill motion-showreel : je ne veux pas la grammaire d'un showreel de motion designer, je veux une vraie pub.
- Surprends-moi. Je ne te donne pas de storyboard.
- Musique et sons calés sur le beat, chaque coupe sur un temps. [Le son signature du produit, par exemple : le son du croquant compte.]
- Rends trois formats : 1920x1080 (YouTube), 1080x1920 (Reels, TikTok), 1080x1080 (LinkedIn, Facebook). Recompose chaque format, ne te contente pas de recadrer. MP4, 60 i/s, dans video-projects/[nom-du-produit]-pub/.

Avant de me la rendre : rends-la, regarde tes propres images, sois impitoyable (est-ce que ça donne envie ? est-ce que le produit est fidèle au vrai ? est-ce que la charte est respectée ? est-ce que chaque seconde pique ?), corrige, et recommence jusqu'à ce que tu sois fier du résultat. Je veux la version 5, pas la version 1.

À la fin, donne-moi : les MP4, le storyboard que tu as choisi en 10 lignes, et les 3 choses que tu as faites sans que je te les demande.
```
