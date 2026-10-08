# Prompt : la vidéo de présentation d'une marque

> À coller dans Claude Code, dossier ouvert = la racine du kit, effort « high ».
> Pas de vidéo de référence, volontairement : la référence, c'est la charte graphique de la marque.
> Pas de charte ? Supprimez le paragraphe et demandez à Claude de la déduire du site.

```text
Fais-moi une vidéo de présentation de 15 secondes (20 maximum) pour cette marque : [URL du site de la marque]
Full motion design. Lâche-toi complètement.

Va sur le site et prends tout ce dont tu as besoin : qui ils sont, ce qu'ils fabriquent, leurs produits, leurs photos, ce qui les rend uniques.
Leur charte graphique est ici, respecte-la à la lettre (logo, couleurs, typos, règles d'usage) :
"[chemin de la charte graphique, PDF]"
"[chemin d'un deuxième document de marque si vous en avez un : brandbook, PPTX...]"
Lis-la en entier, y compris les pages sur les éléments graphiques propres à la marque : c'est ta matière première pour le motion design.

Ce que je veux ressentir en la regardant : "[l'émotion visée, par exemple pour une marque alimentaire : Mais c'est quoi cette marque de fou ? Je veux goûter.]" Du désir, une envie immédiate de découvrir la marque. Un peu de FOMO.

Les règles :
- Court et chargé plutôt que long et vide. Il se passe toujours quelque chose : des éléments qui éclatent, se transforment, se recomposent, des ruptures de rythme. Pas une seule seconde morte.
- Tout se comprend par l'image. Le minimum de texte : le nom de la marque, sa signature, et au plus deux ou trois mots isolés quand ils frappent. Pas de phrases.
- Des images fortes, et le motion design par-dessus pour les rendre encore plus désirables et impactantes. Base-toi sur leurs vraies photos et leurs vrais produits. Si tu génères des images (clés dans le .env), seulement des ambiances ou des matières : jamais un produit, un emballage ou une personne qui n'existe pas.
- N'utilise pas le skill motion-showreel : je ne veux pas la grammaire d'un showreel de motion designer. Je veux une vraie présentation de marque, qui donne envie. Le skill website-to-hyperframes peut t'aider pour capturer le site.
- Surprends-moi. Je ne te donne pas de storyboard. Trouve l'idée visuelle qui n'appartient qu'à cette marque.
- Musique et sons calés sur le beat, chaque coupe sur un temps.
- 1920x1080, 60 i/s, MP4, dans video-projects/[nom-de-la-marque]-presentation/.

Avant de me la rendre : rends-la, regarde tes propres images, sois impitoyable (est-ce que ça donne envie ? est-ce que chaque seconde pique ? est-ce que la charte est respectée ?), corrige, et recommence jusqu'à ce que tu sois fier du résultat. Je veux la version 5, pas la version 1.

À la fin, donne-moi : le MP4, le storyboard que tu as choisi en 10 lignes, et les 3 choses que tu as faites sans que je te les demande.
```
