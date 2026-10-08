# Prompt : le montage d'une vidéo YouTube longue

> À coller dans une nouvelle conversation Claude Code, dossier ouvert = la racine du kit, effort « high ».
> Avant : `npm run new-video -- [nom-de-la-video]`, rushs dans `video-projects/[nom-de-la-video]/assets/raw/`,
> script dans `brief/`. Tournage conseillé : l'écran enregistré avec le micro activé (synchro son contre son),
> et un compte à rebours à voix haute (« trois, deux, un, maintenant ») au lancement de l'enregistrement d'écran.

```text
Tu es le monteur de ma vidéo YouTube. Format long éducatif, environ [durée] minutes, rendu type Nate Herk : clean, premium, face cam et écran qui s'alternent selon ce qui se passe, zooms qui dynamisent, motion design beau et utile. C'est un montage technique : plusieurs sources différentes (face cam, écran, vidéos déjà rendues). Prends le temps de tout comprendre avant de couper.

Le sujet : [le sujet de la vidéo en 2 lignes]. Le spectateur visé : [qui regarde, par exemple un dirigeant de PME, pas un monteur].

## Lis d'abord, dans cet ordre

1. CLAUDE.md, puis .claude/skills/youtube-long-form/SKILL.md et sa référence layouts-and-zooms.md : c'est le pipeline deux sources (face cam + écran), il pilote et te dit quand charger les autres skills du kit.
2. [Optionnel : le dossier d'une vidéo précédente déjà validée, video-projects/[vidéo-précédente]/ (BRIEF.md, DESIGN.md, VERIFY.md). Reprends sa direction artistique pour que les vidéos de la chaîne se ressemblent. Ne recopie pas ses fichiers sans raison.]
3. MOTION_PHILOSOPHY.md avant de toucher aux animations.
4. Le script, ce que je voulais dire section par section : "[chemin du script]"

## Les sources

- Face cam (audio maître) : "[chemin de la face cam]". Ne touche jamais aux originaux.
- Écran : "[chemin de l'enregistrement d'écran]" ([avec / sans] le son du micro).
- Synchro : cale l'écran sur la face cam son contre son si l'écran a du son, sinon sur mon compte à rebours. Vérifie la synchro à l'œil sur 3 moments d'action avant d'aller plus loin.
- Les vidéos déjà rendues, à insérer en plein écran avec leur son (pas à refaire) :
  - "[chemin de la vidéo 1]"
  - "[chemin de la vidéo 2]"
  Regarde dans l'enregistrement d'écran quelles versions j'ai réellement montrées pendant le tournage : ce sont celles-là qui font foi.
- [Optionnel : une vidéo de référence tierce, à créditer à l'écran quand elle apparaît : "[chemin]", auteur : [nom ou @compte].]

## Ce qui compte

- Les mots prononcés font foi. Je m'éloigne toujours du script : sélectionne les prises sur ce que j'ai vraiment dit, garde la meilleure quand il y en a plusieurs, n'affiche que des chiffres que je prononce.
- Le hook (les 45 premières secondes) doit être une démo à lui seul : chaque chose que je cite apparaît à l'écran au moment où je la dis. Quand je dis « regardez cet exemple », la vidéo passe en plein écran, son à fond. Fais-le ultra dynamique.
- Chaque démo : le résultat joué en entier, son à fond, puis ma réaction en face cam. Claude au travail en accéléré quand j'en parle.
- Les zooms servent surtout sur les clics et les résultats qui s'affichent.
- Les CTA : une carte claire, sobre, au moment où je les dis.
- [Ce qui n'est pas encore tourné : garde l'emplacement prévu dans le script avec une carte provisoire, et prévois une insertion simple quand le fichier arrive.]

## Confidentialité (non négociable)

Rien de ceci ne doit être lisible à l'écran : [les noms de vos clients ou de tout ce qui doit rester privé] ; des montants d'un client ; des numéros de téléphone, des emails, des adresses ; mes dossiers et fichiers personnels ; mes onglets et favoris. Floute ou recadre. Contrôle-le sur des images du rendu final, pas seulement dans le plan.

## Comment je veux que tu travailles

- Autonomie maximale. Ne me demande rien que tu peux trouver, mesurer, regarder ou tester toi-même. Les traitements longs (préparation des sources, transcription, rendus) tournent en arrière-plan pendant que tu avances.
- Tu as le feu vert pour la transcription (environ 1 à 2 $) et pour quelques images ou vidéos générées dans le hook ([budget] $ maximum). Toute autre dépense : tu me donnes le coût avant.
- Trois arrêts, pas plus :
  1. Le plan de coupe : section par section, ce que tu gardes, ce que tu jettes, la durée estimée, tes doutes. Court et lisible.
  2. Le hook monté (les 45 premières secondes) : c'est la porte d'entrée du style. Tu ne construis la suite qu'une fois que j'ai validé.
  3. La vidéo complète.
- Avant chaque arrêt : regarde tes propres images, mesure le son, corrige ce qui ne va pas. Je veux voir des versions déjà vérifiées.
- Note chaque décision et chaque contrôle dans VERIFY.md. Travaille dans video-projects/[nom-de-la-video]/.
```
