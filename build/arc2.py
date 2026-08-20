"""Table curseur -> pose, en longueur d'arc perceptive de la tete.

Reprend arc.py, mais travaille sur les 125 poses de assets/lezard.mp4 plutot
que sur les 240 images de la video source, qui n'existent plus :

    ffmpeg -v error -y -i assets/lezard.mp4 -vsync 0 build/poses/%03d.png

Principe : on mesure ce qui bouge reellement d'une pose a la suivante, sur la
tete seule, et le curseur parcourt cette somme cumulee lineairement. Le
mouvement percu est ainsi proportionnel au deplacement du curseur, au lieu de
suivre l'inegalite du tournage (36 % du mouvement dans les 20 premieres poses,
2 % dans les 20 suivantes).

Trois reperes sont ancres : u = -1 sur la pose 0, u = 0 sur la pose de face,
u = +1 sur la derniere pose.
"""

import json
import os
import sys

import numpy as np
from PIL import Image

DOSSIER = os.path.dirname(os.path.abspath(__file__))
POSES = os.path.join(DOSSIER, "poses")

# la tete seule : c'est elle qui doit commander, pas la derive du corps.
# ROI d'arc.py (x 440-870 dans la video source) ramenee au recadrage 900x720.
ROI = (slice(20, 300), slice(290, 720))
BRUIT = 6.0 / 255.          # plancher : en-deca, c'est du grain video

# Pose de face : relevee sur planche de tetes recentrees sur la silhouette.
# La zone franchement frontale va de la pose 20 a la pose 40 ; 30 en est le
# milieu. arc.py retenait 20, en bord de zone : le lezard restait legerement
# tourne quand le curseur etait a son aplomb.
FACE = 30

N = 401                     # entrees de la table, de u = -1 a u = +1


def charger(i):
    chemin = os.path.join(POSES, "%03d.png" % (i + 1))
    return np.asarray(Image.open(chemin).convert("RGB")).astype(np.float32) / 255.


def main():
    nb = len([f for f in os.listdir(POSES) if f.endswith(".png")])
    if nb == 0:
        sys.exit("aucune pose dans build/poses/ — extraire les images d'abord")

    precedent = charger(0)
    pas = []
    for i in range(1, nb):
        courant = charger(i)
        ecart = np.abs(courant - precedent).max(-1)[ROI]
        pas.append(float(np.clip(ecart - BRUIT, 0, None).sum()))
        precedent = courant

    arc = np.concatenate([[0.0], np.cumsum(pas)])
    arc /= arc[-1]

    lut = []
    for k in range(N):
        u = k / (N - 1) * 2 - 1
        cible = arc[FACE] * (1 + u) if u < 0 else arc[FACE] + (1 - arc[FACE]) * u
        lut.append(int(np.argmin(np.abs(arc - cible))))

    sauts = [lut[i + 1] - lut[i] for i in range(len(lut) - 1)]
    print("poses :", nb, " face :", FACE, " arc au repere de face : %.3f" % arc[FACE])
    print("poses distinctes utilisees :", len(set(lut)), "/", nb)
    print("saut max entre deux entrees voisines :", max(sauts), "poses")
    print("premieres :", lut[:5], "  centre :", lut[198:203], "  dernieres :", lut[-5:])

    json.dump({"fps": 25, "count": nb, "front": FACE, "lut": lut},
              open(os.path.join(DOSSIER, "poses.json"), "w"))


if __name__ == "__main__":
    main()
