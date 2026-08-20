# Lézard qui suit le curseur

**En ligne : https://jgrewis.github.io/animation-lezard/**

Page d'arrivée : une seule phrase, et le lézard de la vidéo source qui tourne la
tête vers le curseur. Le décor autour de lui **est celui de la vidéo** — aucun
détourage, donc aucune découpe à voir.

## Ouvrir

```bash
python3 build/serve.py 4173
```

puis `http://localhost:4173`.

> Ne pas servir le dossier avec `python3 -m http.server` : ce serveur ignore
> l'en-tête `Range`, le navigateur déclare alors la vidéo non déplaçable et le
> lézard reste figé sur sa première pose. `build/serve.py` ajoute ce qu'il faut.
> Un hébergement normal (Ionos, Apache, nginx) gère `Range` nativement.

Par double-clic sur `index.html`, la page fonctionne aussi : le script est un
script classique, pas un module ES, précisément pour cela.

## Mise en ligne

Le site est publié par **GitHub Pages**, branche `main`, racine du dépôt. Il n'y
a rien à construire : pousser sur `main` suffit, la mise à jour prend une minute.

```bash
git add -A && git commit -m "…" && git push
```

Point vérifié avant tout le reste : **GitHub Pages répond bien en
`206 Partial Content`** sur `assets/lezard.mp4`, avec `accept-ranges: bytes`.
C'est la condition du suivi — sans elle, la vidéo n'est pas déplaçable et le
lézard reste figé sur la pose de face (voir plus bas). Contrôle en une ligne :

```bash
curl -s -D - -o /dev/null -r 100-200 https://jgrewis.github.io/animation-lezard/assets/lezard.mp4 | head -3
```

## Comment ça marche

Le personnage n'est pas redessiné : ce sont **ses propres images**.

1. **Une seule prise** de la vidéo est exploitable : les images 104 à 228, où la
   tête balaie sans coupure jusqu'au profil droit. Elles sont recadrées en
   900 × 720 et réencodées **tout-image-clé** dans `assets/lezard.mp4` : 125
   poses, 25 i/s, 5 s exactement. La pose *i* est à `currentTime = (i+0,5)/25`.
2. **Le fond continue le décor.** `assets/decor.webp` est une plaque 2480 × 1620 :
   le décor de la vidéo, vidé du personnage puis prolongé. Le cadre vidéo se
   pose dessus à sa place exacte — coin haut-gauche à (450, 700) — et ses quatre
   bords sont fondus au masque pour absorber le résidu de grain.
3. **Le curseur choisit la pose** par une table de 401 entrées calculée en
   longueur d'arc perceptive de la tête (`build/arc2.py`). Le mouvement perçu est
   ainsi proportionnel au déplacement du curseur, alors que le tournage, lui, est
   très inégal : 37 % du mouvement tient dans les 20 premières poses.
4. **La hauteur du curseur** fait répondre le corps, pas la tête : la vidéo ne
   contient aucun mouvement de tête vertical. La scène entière — plaque et cadre
   vidéo ensemble — se déplace et s'incline très légèrement, ce qui garde le
   raccord intact par construction.

## Le piège de la colorimétrie

Sans balises de couleur, ffmpeg décodait la vidéo en **BT.601** et Chrome en
**BT.709** : le décor de la vidéo ressortait 10/255 plus clair que la plaque, et
le cadre se voyait comme un rectangle posé sur le fond. `build/etiqueter.sh`
inscrit les bonnes balises — matrice BT.601, primaires et courbe sRGB — sans
réencoder. Écart après correction : **1,6/255 en moyenne, 4 au pire**.

Les primaires comptent autant que la matrice : étiquetées en 601, elles
déclenchent une conversion à l'affichage et le rectangle réapparaît — invisible,
lui, dans une lecture `canvas`.

## Réglages utiles

| Où | Quoi |
|---|---|
| `styles.css` → `--cadre-l` | taille du personnage (tout le reste en découle) |
| `styles.css` → `--cadre-gauche`, `--cadre-bas` | position du cadre vidéo dans la fenêtre |
| `styles.css` → `--voile` | densité du halo sous la phrase (contraste) |
| `script.js` → `viser()` | amplitude du suivi |
| `script.js` → `repos()` | comportement quand le curseur ne bouge plus (4 s) |
| `script.js` → `SOUPLESSE_TETE` | nervosité du suivi (11 = vif, 4 = paresseux) |
| `script.js` → `POUSSEE`, `BASCULE` | amplitude de la réponse verticale |

## Fichiers

```
index.html
styles.css
script.js                     table des poses incluse (aucun fetch : marche en file://)
assets/lezard.mp4    1 992 Ko 125 poses, tout-image-clé, 900 × 720
assets/decor.webp       32 Ko plaque de fond 2480 × 1620
assets/pose-face.webp   31 Ko pose de face : premier affichage, et repli si la vidéo échoue

build/serve.py                serveur de développement gérant Range
build/arc2.py                 calcul de la table curseur → pose
build/poses.json              la table (source de vérité de celle de script.js)
build/lisser.py               lissage de la plaque
build/plate2.py               fabrication de la plaque brute
build/scipy_free.py           utilitaires de plate2.py
build/etiqueter.sh            balises de couleur de la vidéo
build/decor.json              géométrie de la plaque
build/decor-brut.webp         plaque avant lissage
build/lezard-sans-tags.mp4    vidéo avant étiquetage

_precedent/                   version précédente, au lézard détouré
Changements__Le_lézard_doit.mp4   vidéo source
```

Total servi : **2,1 Mo**, dont 2,0 Mo de vidéo. Ce poids est un choix : le
tout-image-clé garantit l'exactitude du déplacement sur tous les navigateurs.

## Refaire la chaîne

```bash
mkdir -p build/poses                                                  # dossier de travail
ffmpeg -v error -y -i assets/lezard.mp4 -vsync 0 build/poses/%03d.png  # les 125 poses
python3 build/arc2.py          # -> build/poses.json
python3 build/lisser.py        # build/decor-brut.webp -> assets/decor.webp
sh build/etiqueter.sh          # balises de couleur de la vidéo
```

La table de `script.js` est une copie de `build/poses.json` : après `arc2.py`,
il faut la recopier dans le tableau `LUT`.
