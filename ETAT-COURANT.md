# État courant — 20 août 2026, 10 h

Projet : page d'arrivée « L'Animation de votre site web passe à un autre niveau »,
avec le lézard de la vidéo qui suit le curseur.
Plan de référence : [`PLAN-lezard-fond-origine.md`](PLAN-lezard-fond-origine.md)

---

## En une phrase

**La page est écrite et recettée : T2 à T7 sont faites.**
Le fond, le suivi, la réponse verticale, les états de panne et le rendu de
375 px à 1920 px sont vérifiés, mesures à l'appui. Reste un point qui ne peut pas
l'être ici : le ressenti en mouvement réel (voir « Ce qui n'a pas pu être vérifié »).

---

## Où on en est, tranche par tranche

| Tranche | État | Détail |
|---|---|---|
| T0 — Sauvegarde | ✅ | `_precedent/` |
| T1 — Fabrication des médias | ✅ | plus étiquetage colorimétrique et lissage de la plaque |
| T2 — Squelette qui marche | ✅ | validé, puis fondu dans la page réelle |
| T3 — Fond et raccord | ✅ | écart mesuré 1,6/255 |
| T4 — Typographie et mise en page | ✅ | contraste mesuré 5,3:1 |
| T5 — Réponse verticale | ✅ | par la scène entière |
| T6 — États et robustesse | ✅ | chargement, échec vidéo, seek impossible, tactile |
| T7 — Recette | ✅ | 375 / 640 / 768 / 1024 / 1280 / 1920 |

---

## Les trois défauts trouvés en route

Ce sont eux qui ont pris le temps ; ils sont tous corrigés.

### 1. Le serveur de développement rendait la vidéo non déplaçable

`python3 -m http.server` ignore l'en-tête `Range`. Chrome déclarait alors
`video.seekable` vide, et **tout `currentTime` retombait à 0** : le lézard restait
figé sur sa première pose. Le diagnostic était trompeur — la vidéo se chargeait,
l'image s'affichait, aucune erreur en console.

→ [`build/serve.py`](build/serve.py) répond en `206 Partial Content`.
Un hébergement normal gère `Range` : le défaut était local, mais il masquait tout
le reste. Le script sait maintenant reconnaître ce cas et se rabattre proprement.

### 2. La vidéo et la plaque n'étaient pas décodées dans la même colorimétrie

Aucune balise de couleur dans le fichier : ffmpeg (qui a servi à fabriquer la
plaque) décodait en **BT.601**, Chrome en **BT.709**. Le décor de la vidéo
ressortait **10/255 plus clair** que la plaque — le cadre se voyait comme un
rectangle posé sur le fond. C'était la vraie cause du raccord raté, pas le grain.

Détail à retenir : corriger la seule matrice ne suffit pas. Étiquetées en 601,
**les primaires** déclenchent une conversion de gestion des couleurs à
l'affichage, et le rectangle réapparaît — alors qu'une lecture `canvas` le dit
corrigé. Bon étiquetage : matrice BT.601, primaires et courbe **sRGB**.

→ [`build/etiqueter.sh`](build/etiqueter.sh), sans réencodage.
**Écart final : 1,6/255 en moyenne, 4 au pire.** Invisible.

### 3. Le repère de face était décalé

`poses.json` plaçait la pose de face à l'index 20. Sur une planche de têtes
recentrées sur la silhouette, la zone franchement frontale va de la pose 20 à la
pose 40 : l'index 20 en est le bord. Curseur à l'aplomb du lézard, celui-ci
restait donc légèrement tourné.

→ **face = 30**, table refaite par [`build/arc2.py`](build/arc2.py). Le saut
maximal entre deux entrées voisines tombe à 2 poses (117 poses distinctes sur
125). Vérifié à l'écran : curseur au-dessus de la tête, le lézard regarde droit.

> Deux métriques automatiques de symétrie ont été essayées et **écartées** : la
> symétrie de silhouette (déjà écartée en T1) et la largeur comparée des deux
> verres de lunettes, qui fusionnent en une seule tache sombre. Le repère est
> tranché à l'œil, sur une planche recentrée — c'est l'instrument juste ici.

---

## Ce qui a été mesuré

| Quoi | Mesure | Seuil |
|---|---|---|
| Raccord vidéo / plaque | 1,6/255 moyen, 4 max | invisible en dessous de ~5 |
| Contraste du texte, 1920 × 1080 | 5,28:1 | 4,5:1 |
| Contraste du texte, 1280 × 800 | 5,35:1 | 4,5:1 |
| Contraste du texte, portrait | 9,88:1 | 4,5:1 |
| Débordement horizontal à 375 px | aucun (`scrollWidth` = `clientWidth` = 375) | — |
| Console et réseau | aucune erreur, aucun 404 | — |
| Poids servi | 2,1 Mo (dont 2,0 de vidéo) | choix validé |

Le contraste est mesuré à la position réelle du texte : la plaque est lue pixel
par pixel sous la boîte du titre, le halo est appliqué par-dessus, et on garde le
pire point. Sans halo, le point le plus clair traversé par le texte tombait à
**3,2:1**.

---

## Deux écarts au plan, assumés

1. **Le fond n'est pas un dégradé CSS** (Dec-3) mais une plaque image de 32 Ko.
   Un dégradé ne reproduit ni la ligne d'horizon ni la retombée de lumière du
   studio : le raccord se voyait. La plaque, elle, *est* le décor.
2. **La table des poses n'est pas chargée depuis un JSON** (§5 du plan) mais
   écrite dans `script.js`. Un `fetch` échoue en `file://` — la page ne
   marcherait plus par double-clic — et c'est une requête de plus pour 1,2 Ko.
   `build/poses.json` reste la source de vérité ; la copie est vérifiée à chaque
   régénération.

---

## Ce qui n'a pas pu être vérifié ici

Le navigateur de l'atelier garde son panneau masqué : `document.visibilityState`
reste `hidden`, et **`requestAnimationFrame` ne tourne pas** hors capture d'écran.
Le suivi a donc été vérifié pose par pose (positions extrêmes, pose de face,
signe de la réponse verticale, valeurs des variables CSS), mais **la fluidité en
mouvement continu ne l'a pas été**.

À faire à la main, en ouvrant la page :

- balayer lentement l'écran de gauche à droite : aucun saut ne doit se voir ;
- s'arrêter : le lézard doit continuer de regarder autour de lui, doucement ;
- monter et descendre le curseur : le corps répond, le regard reste horizontal ;
- vérifier sur un vrai téléphone, sans souris : le balayage lent doit démarrer seul.

Si un saut se voit au balayage, le réglage est `SOUPLESSE_TETE` dans `script.js`.

---

## Mise en ligne

Publié sur **GitHub Pages** le 20 août 2026 :

- dépôt : https://github.com/jgrewis/animation-lezard (public, branche `main`)
- site : **https://jgrewis.github.io/animation-lezard/**

Vérifié en ligne, pas seulement en local : la vidéo est déplaçable
(`seekable` = [0, 5]), la page passe bien en `scene--prete`, aucune ressource en
erreur. GitHub Pages répond en `206 Partial Content` avec `accept-ranges: bytes`
— c'est ce qui manquait au serveur de développement et qui figeait tout.

Toute mise à jour se fait par un `git push` sur `main`.

---

## Reste à faire

- [ ] Recette humaine en mouvement (ci-dessus)
- [ ] `prefers-reduced-motion` : le code le traite (ni animation d'entrée, ni
      dérive au repos, ni bascule), **mais l'atelier ne sait pas l'émuler** —
      à vérifier en activant l'option système
- [ ] Mise en ligne, le jour venu, par la procédure Ionos

Fait au passage : `assets/lezard.webp` (planche de l'ancienne version) et la démo
T2 sont supprimés, `README.md` est réécrit.
