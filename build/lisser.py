"""Lissage de la plaque de fond.

`plate2.py` produit une plaque brute (`build/decor-brut.webp`) : le decor de la
video vide de son personnage, puis prolonge. Le remplissage laisse, juste a
droite du cadre video, des taches et des raccords rectangulaires visibles sur un
fond de studio aussi lisse. Un flou gaussien de 20 px les efface sans toucher au
degrade ni a la ligne d'horizon.

Mesure a l'appui : sur l'anneau qui longe le cadre video, le flou ne deplace la
couleur que de 1,3/255 en moyenne (p99 = 6) — bien en dessous du residu de grain
de 4/255 deja constate entre la video et la plaque. Le raccord n'est donc pas
degrade, et la plaque passe de 204 Ko a 33 Ko.

    python3 build/lisser.py
"""

from PIL import Image, ImageFilter

RAYON = 20
SOURCE = "build/decor-brut.webp"
CIBLE = "assets/decor.webp"

if __name__ == "__main__":
    plaque = Image.open(SOURCE).convert("RGB").filter(ImageFilter.GaussianBlur(RAYON))
    plaque.save(CIBLE, quality=92, method=6)
    print(f"{CIBLE} : {plaque.size[0]}x{plaque.size[1]}")
