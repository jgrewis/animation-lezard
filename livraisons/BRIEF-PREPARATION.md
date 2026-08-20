# Brief — préparation d'une nouvelle prise

Tâche mécanique et bornée. **Tu prépares et tu mesures, tu ne juges pas.** Aucun
verdict sur la qualité de la matière : tu rapportes des chiffres, quelqu'un
d'autre décide.

Modèle conseillé : `claude-sonnet-5`.

---

## Ce qu'on te donne

Un fichier vidéo. Rien d'autre.

## Ce que tu rends

Un dossier `livraisons/<AAAA-MM-JJ>-<mot-clef>/` contenant :

```
source.mp4          la vidéo telle que reçue, renommée
images/0001.png …   toutes ses images
PROBE.txt           la fiche technique du fichier
RAPPORT.md          ton compte rendu
```

Et une ligne ajoutée à `livraisons/INDEX.md` (à créer s'il n'existe pas).

---

## Les étapes, dans l'ordre

### 1. Ranger

```bash
mkdir -p "livraisons/<AAAA-MM-JJ>-<mot-clef>/images"
cp "<la vidéo>" "livraisons/<AAAA-MM-JJ>-<mot-clef>/source.mp4"
```

Le mot-clef décrit la prise en un mot : `ligne-haute`, `regard-vertical`,
`clignements`… Demande-le si ce n'est pas évident.

### 2. Fiche technique

```bash
ffprobe -v error -select_streams v:0 -show_entries \
  stream=width,height,r_frame_rate,nb_frames,pix_fmt,color_range,color_space,color_primaries,color_transfer \
  -of default=noprint_wrappers=1 "livraisons/<dossier>/source.mp4" | tee "livraisons/<dossier>/PROBE.txt"
```

Si `color_space` vaut `unknown` : **note-le dans le rapport, ne corrige rien.**
L'étiquetage dépend de la façon dont la vidéo a été produite, ce n'est pas à toi
de le deviner.

### 3. Extraire les images

```bash
ffmpeg -v error -y -i "livraisons/<dossier>/source.mp4" -vsync 0 \
  "livraisons/<dossier>/images/%04d.png"
ls "livraisons/<dossier>/images" | wc -l
```

Le nombre d'images doit correspondre à `nb_frames`. Sinon, signale l'écart.

### 4. Mesures de compatibilité avec la prise existante

C'est le point qui compte : les nouvelles images seront **cumulées** avec les
125 existantes. Si le fond, l'échelle ou la couleur diffèrent, le personnage
changera discrètement de tête au milieu du suivi.

Exécute ce bloc tel quel, en remplaçant `<dossier>` :

```bash
python3 - <<'PY'
import numpy as np, os
from PIL import Image
D = "livraisons/<dossier>/images"

def mesures(chemin):
    a = np.asarray(Image.open(chemin).convert("RGB")).astype(np.float32)
    h, w, _ = a.shape
    c = 60
    fond = np.concatenate([a[:c,:c].reshape(-1,3), a[:c,-c:].reshape(-1,3)])
    r, g, b = a[...,0], a[...,1], a[...,2]
    perso = g > r * 0.62                      # le vert du personnage sur l'orange
    ys, xs = np.nonzero(perso)
    return {
        "taille": (w, h),
        "fond_coins_RVB": [round(v,1) for v in fond.mean(0)],
        "perso_largeur_px": int(xs.max()-xs.min()) if len(xs) else 0,
        "perso_hauteur_px": int(ys.max()-ys.min()) if len(ys) else 0,
        "perso_centre_x": int(xs.mean()) if len(xs) else 0,
    }

noms = sorted(f for f in os.listdir(D) if f.endswith(".png"))
print("NOUVELLE PRISE")
for nom in (noms[0], noms[len(noms)//2], noms[-1]):
    print(" ", nom, mesures(os.path.join(D, nom)))
print("REFERENCE (pose de face de la prise actuelle)")
print("  pose-de-face.png", mesures("reference/pose-de-face.png"))
PY
```

Recopie la sortie **telle quelle** dans le rapport. Ne l'interprète pas.

### 5. Calibration du suivi de l'œil

```bash
rm -rf build/images && cp -r "livraisons/<dossier>/images" build/images
python3 build/analyse.py calibrer
```

Ouvre `build/calibration-grille.png` : c'est la première image, quadrillée, avec
les coordonnées en rouge tous les 200 px et un trait vert tous les 50 px.
**Regarde-la** et relève la boîte autour de l'œil du personnage le plus visible,
sous la forme `x,y,largeur,hauteur` — coin haut-gauche, puis dimensions. Une
boîte serrée sur l'œil, environ 120 × 110 px pour une image de 900 px de large.

Puis :

```bash
python3 build/analyse.py mesurer --oeil <x,y,largeur,hauteur> | tee "livraisons/<dossier>/MESURES.txt"
```

Recopie la sortie complète dans le rapport, **y compris la grille de couverture
et le score de calage du suivi**. Si le score médian est inférieur à 0,6, le
suivi a décroché : réessaie avec une autre boîte, un peu plus grande et mieux
centrée, et dis-le dans le rapport.

### 6. Rapport

`livraisons/<dossier>/RAPPORT.md`, dans cet ordre, sans commentaire de qualité :

1. nom du fichier reçu, date, mot-clef
2. la fiche technique (étape 2), et la mention si les balises de couleur manquent
3. nombre d'images extraites, et l'écart éventuel avec `nb_frames`
4. la sortie brute de l'étape 4
5. la boîte de l'œil retenue, et la sortie brute de l'étape 5
6. tout ce qui a échoué ou surpris

Puis une ligne dans `livraisons/INDEX.md` :

```
| AAAA-MM-JJ | mot-clef | N images | LxH | balises couleur : oui/non | couverture : X % de cases vides |
```

### 7. Commit

```bash
git add livraisons reference .gitignore
git commit -m "Prépare la prise <mot-clef> du <date>"
git push
```

Les images et la vidéo source sont ignorées par git (voir `.gitignore`) :
**seuls les rapports sont versionnés.** C'est voulu, ne force pas l'ajout.

---

## Ce que tu ne fais pas

- Ne touche pas à `index.html`, `styles.css`, `script.js`, `assets/`.
- Ne réétiquette pas la vidéo, ne la réencode pas, ne la recadre pas.
- Ne supprime pas les images de la prise précédente.
- Ne modifie pas les seuils en tête de `build/analyse.py`.
- Ne donne pas d'avis sur la qualité de la prise. Les chiffres suffisent.

## Si quelque chose bloque

Dis-le dans le rapport et arrête-toi là. Une étape ratée signalée vaut mieux
qu'une étape contournée en silence.

---

## Pour mémoire : à quoi ça sert

Les images de toutes les prises seront **mises en commun** pour former une
banque de poses. Le site n'y cherchera pas « la pose numéro N » mais « la pose
qui regarde dans cette direction ». D'où l'importance des mesures de l'étape 4 :
deux prises incompatibles donnent un personnage qui change d'aspect en cours de
suivi.

`reference/pose-de-face.png` est l'image de référence de la prise actuelle. Elle
sert aussi d'image de départ pour générer les prises suivantes, ce qui garde la
lumière, le cadrage et l'identité du personnage.
