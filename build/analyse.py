"""Recette de la matière source, et relevé de la direction du regard.

Le script mesure et rapporte. Il ne décide pas : les seuils qui séparent le bon
du mauvais sont fixés une seule fois, après avoir regardé, puis figés en tête de
fichier. C'est l'inverse de ce qui a été fait la première fois, où des seuils
inventés ont tranché à la place de l'œil — et se sont trompés deux fois.

Trois commandes, dans cet ordre :

    python3 build/analyse.py extraire ma-video.mp4
    python3 build/analyse.py calibrer
    python3 build/analyse.py mesurer --oeil 430,70,150,120

`calibrer` produit deux images à regarder : une planche contact de toutes les
poses, et la première image quadrillée pour y lire les coordonnées de l'œil.
`mesurer` sort un rapport en texte — c'est lui qu'on transmet, pas les images.

Ne demande que numpy et Pillow. L'extraction demande ffmpeg.
"""

import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

DOSSIER = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(DOSSIER, "images")

# ------------------------------------------------------------------ seuils
# À revoir une fois, en regardant, puis à ne plus toucher.
DERIVE_FOND_MAX = 3.0        # /255, entre la première et la dernière image
TRANSLATION_MAX = 2.0        # px, déplacement du personnage dans le cadre
PAS_IRREGULIER = 2.0         # x la médiane, au-delà le balayage saccade
SPECULAIRE_MAX = 240         # /255 : au-dela, un pixel est considere sature
SPECULAIRE_PART = 0.10       # fraction de la boite saturee au-dela de laquelle le verre masque l'oeil
NETTETE_MIN = 0.35           # en dessous, plus de pupille lisible : à calibrer en regardant


def images():
    fichiers = sorted(f for f in os.listdir(IMAGES) if f.endswith(".png"))
    if not fichiers:
        sys.exit("aucune image dans build/images/ — lancer « extraire » d'abord")
    return fichiers


def charger(nom, gris=False):
    im = Image.open(os.path.join(IMAGES, nom)).convert("RGB")
    return im.convert("L") if gris else im


def hautes_frequences(im):
    """Enlève le fond lisse, garde les arêtes : lunettes, écailles, contours."""
    a = np.asarray(im, dtype=np.float32)
    flou = np.asarray(im.filter(ImageFilter.GaussianBlur(6)), dtype=np.float32)
    return a - flou


ECHELLE = 3          # on suit sur une image réduite : 3 px de précision suffisent
FENETRE = 10         # rayon de recherche autour de la position précédente, réduite


def reduire(a):
    h = (a.shape[0] // ECHELLE) * ECHELLE
    w = (a.shape[1] // ECHELLE) * ECHELLE
    return a[:h, :w].reshape(h // ECHELLE, ECHELLE, w // ECHELLE, ECHELLE).mean((1, 3))


def suivre(gabarit, cible, depart):
    """Position du gabarit dans l'image, par moindres carrés normalisés.

    Trois précautions, apprises d'essais ratés :

    - la corrélation est **normalisée**, sinon elle se cale sur la zone la plus
      contrastée de l'image et non sur le motif ;
    - la recherche est **bornée** autour de la position précédente : l'œil ne
      saute pas d'un bout à l'autre entre deux images ;
    - le gabarit est **repris à chaque image** (voir `mesurer`). Un gabarit figé
      ne survit pas à 130° de rotation : l'œil de profil ne ressemble en rien à
      l'œil de face, et le suivi décroche dès le premier quart du balayage.
    """
    g = reduire(gabarit)
    g = (g - g.mean()) / (g.std() + 1e-6)
    gh, gw = g.shape
    c = reduire(cible)
    x0, y0 = depart[0] // ECHELLE, depart[1] // ECHELLE
    best, pos = -2.0, (x0, y0)
    for dy in range(-FENETRE, FENETRE + 1):
        for dx in range(-FENETRE, FENETRE + 1):
            x, y = x0 + dx, y0 + dy
            if x < 0 or y < 0 or y + gh > c.shape[0] or x + gw > c.shape[1]:
                continue
            z = c[y:y + gh, x:x + gw]
            s = z.std()
            if s < 1e-6:
                continue
            score = float((((z - z.mean()) / s) * g).mean())
            if score > best:
                best, pos = score, (x, y)
    return pos[0] * ECHELLE, pos[1] * ECHELLE, best


def oeil_et_pupille(z):
    """Dans la boîte de l'œil : le globe, puis la pupille à l'intérieur.

    Le globe (sclère et iris) est nettement plus clair que la peau et que la
    monture. La pupille est une tache sombre *à l'intérieur* de ce globe — c'est
    cette imbrication qui distingue « pupille visible » de « œil roulé, dôme
    uniforme ». Chercher simplement « le plus sombre de la boîte » ne marche
    pas : on retrouve la monture des lunettes à tous les coups.
    """
    globe = z > np.percentile(z, 72)
    ys, xs = np.nonzero(globe)
    if len(xs) < 40:
        return None
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    marge_y = max(1, (y1 - y0) // 6)
    marge_x = max(1, (x1 - x0) // 6)
    interieur = z[y0 + marge_y:y1 - marge_y + 1, x0 + marge_x:x1 - marge_x + 1]
    if interieur.size < 25:
        return None
    clair = float(np.median(z[globe]))
    # netteté : de combien le cœur sombre tranche sur le globe clair.
    # 0 = dôme uniforme, aucun regard lisible ; 1 = pupille franchement noire.
    nettete = float(1 - np.percentile(interieur, 4) / max(clair, 1e-6))
    sombre = interieur < clair * 0.55
    aire = int(sombre.sum())
    if aire < 6:
        return None, clair, nettete
    py, px = np.nonzero(sombre)
    return ((x0 + marge_x + px.mean()) / z.shape[1],
            (y0 + marge_y + py.mean()) / z.shape[0], aire), clair, nettete


# ------------------------------------------------------------------ commandes

def extraire(video):
    os.makedirs(IMAGES, exist_ok=True)
    for f in os.listdir(IMAGES):
        os.remove(os.path.join(IMAGES, f))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vsync", "0",
                    os.path.join(IMAGES, "%04d.png")], check=True)
    sonde = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,nb_frames,color_range,color_space,"
         "color_primaries,color_transfer", "-of", "json", video],
        capture_output=True, text=True, check=True)
    flux = json.loads(sonde.stdout)["streams"][0]
    print("%d images extraites" % len(images()))
    for cle in ("width", "height", "r_frame_rate", "nb_frames", "color_range",
                "color_space", "color_primaries", "color_transfer"):
        print("  %-18s %s" % (cle, flux.get(cle, "—")))
    if flux.get("color_space") in (None, "unknown"):
        print("\n  /!\\ aucune balise de couleur : à réétiqueter avec build/etiqueter.sh")


def calibrer():
    noms = images()
    # 1. planche contact de toutes les poses
    pas = max(1, len(noms) // 120)
    choix = noms[::pas]
    vign = charger(choix[0]).size
    L = 160
    H = int(L * vign[1] / vign[0])
    cols = 10
    rows = (len(choix) + cols - 1) // cols
    pl = Image.new("RGB", (L * cols, H * rows), (0, 0, 0))
    d = ImageDraw.Draw(pl)
    for k, nom in enumerate(choix):
        x, y = (k % cols) * L, (k // cols) * H
        pl.paste(charger(nom).resize((L, H)), (x, y))
        d.text((x + 3, y + 2), nom[:-4], fill=(255, 255, 0))
    pl.save(os.path.join(DOSSIER, "calibration-planche.png"))

    # 2. première image quadrillée, pour y lire les coordonnées de l'œil
    im = charger(noms[0]).copy()
    d = ImageDraw.Draw(im)
    for x in range(0, im.width, 50):
        d.line([(x, 0), (x, im.height)], fill=(0, 255, 0) if x % 200 else (255, 0, 0))
        if x % 200 == 0:
            d.text((x + 3, 3), str(x), fill=(255, 0, 0))
    for y in range(0, im.height, 50):
        d.line([(0, y), (im.width, y)], fill=(0, 255, 0) if y % 200 else (255, 0, 0))
        if y % 200 == 0:
            d.text((3, y + 3), str(y), fill=(255, 0, 0))
    im.save(os.path.join(DOSSIER, "calibration-grille.png"))

    print("build/calibration-planche.png  — toutes les poses, à parcourir des yeux")
    print("build/calibration-grille.png   — y lire la boîte autour de l'œil proche")
    print()
    print("puis : python3 build/analyse.py mesurer --oeil x,y,largeur,hauteur")


def mesurer(boite):
    noms = images()
    ox, oy, ow, oh = boite
    ref = charger(noms[0], gris=True)
    gabarit = hautes_frequences(ref)[oy:oy + oh, ox:ox + ow]
    MAJ_GABARIT = 0.5      # part de l'image courante reprise dans le gabarit

    suivi, pupilles, speculaire, scores, nettetes = [], [], [], [], []
    depart = (ox, oy)
    for nom in noms:
        gr = charger(nom, gris=True)
        hf = hautes_frequences(gr)
        x, y, score = suivre(gabarit, hf, depart)
        depart = (x, y)
        suivi.append((x, y))
        scores.append(round(score, 3))
        # le motif se déforme au fil de la rotation : on le laisse suivre,
        # en gardant une part de l'ancien pour freiner la dérive
        vu = hf[y:y + oh, x:x + ow]
        if vu.shape == gabarit.shape:
            gabarit = (1 - MAJ_GABARIT) * gabarit + MAJ_GABARIT * vu
        z = np.asarray(gr, dtype=np.float32)[y:y + oh, x:x + ow]
        if z.size == 0:
            pupilles.append(None); speculaire.append(0); continue
        speculaire.append(float((z > SPECULAIRE_MAX).mean()))
        trouve = oeil_et_pupille(z)
        if trouve is None:
            pupilles.append(None); nettetes.append(0.0)
        else:
            pupilles.append(trouve[0])
            nettetes.append(round(trouve[2], 3))

    xs = np.array([p[0] for p in suivi], dtype=float)
    ys = np.array([p[1] for p in suivi], dtype=float)
    aires = np.array([p[2] if p else 0 for p in pupilles], dtype=float)
    med_aire = np.median(aires[aires > 0]) if (aires > 0).any() else 0

    # --- fond : coins de la première et de la dernière image
    a0 = np.asarray(charger(noms[0]), dtype=np.float32)
    a1 = np.asarray(charger(noms[-1]), dtype=np.float32)
    c = 80
    coins = np.concatenate([
        np.abs(a0[:c, :c] - a1[:c, :c]).ravel(),
        np.abs(a0[:c, -c:] - a1[:c, -c:]).ravel(),
        np.abs(a0[-c:, :c] - a1[-c:, :c]).ravel(),
        np.abs(a0[-c:, -c:] - a1[-c:, -c:]).ravel()])
    derive = float(coins.mean())

    # le suivi est quantifié à ECHELLE px : on mesure le pas sur 5 images pour
    # que la quantification ne noie pas l'irrégularité qu'on cherche
    FENETRE_PAS = 5
    pas = np.abs(xs[FENETRE_PAS:] - xs[:-FENETRE_PAS]) / FENETRE_PAS
    med_pas = float(np.median(pas)) if len(pas) else 0
    irregulier = [i + 1 for i, v in enumerate(pas) if med_pas and v > PAS_IRREGULIER * med_pas]
    sans_pupille = [i for i, p in enumerate(pupilles) if p is None]
    reflets = [i for i, s in enumerate(speculaire) if s > SPECULAIRE_PART]

    def verdict(ok):
        return "OK  " if ok else "NON "

    print("=" * 64)
    print("RECETTE DE LA MATIERE — %d images" % len(noms))
    print("=" * 64)
    print("%s derive du fond          %5.2f /255   (seuil %.0f)"
          % (verdict(derive <= DERIVE_FOND_MAX), derive, DERIVE_FOND_MAX))
    print("%s amplitude horizontale   %5.0f px      (course de l'oeil suivi)"
          % ("    ", xs.max() - xs.min()))
    print("%s amplitude verticale     %5.0f px"
          % ("    ", ys.max() - ys.min()))
    p90 = float(np.percentile(pas, 90)) if len(pas) else 0
    print("%s regularite du balayage  pas median %.1f px, p90 %.1f, max %.1f  (rapport %.1f)"
          % (verdict(med_pas and pas.max() <= PAS_IRREGULIER * med_pas),
             med_pas, p90, float(pas.max()) if len(pas) else 0,
             float(pas.max() / med_pas) if med_pas else 0))
    if irregulier[:12]:
        print("       images concernees : %s%s"
              % (irregulier[:12], " ..." if len(irregulier) > 12 else ""))
    print("%s pupille visible         %d image(s) sans pupille"
          % (verdict(not sans_pupille), len(sans_pupille)))
    if sans_pupille[:12]:
        print("       images concernees : %s%s"
              % (sans_pupille[:12], " ..." if len(sans_pupille) > 12 else ""))
    net = np.array(nettetes, dtype=float)
    faibles = sorted(range(len(net)), key=lambda i: net[i])[:10]
    print("%s nettete de la pupille   mediane %.2f, minimum %.2f"
          % (verdict(net.min() > NETTETE_MIN), float(np.median(net)), float(net.min())))
    print("       les 10 images les plus faibles : %s"
          % ", ".join("%d (%.2f)" % (i, net[i]) for i in sorted(faibles)))
    print("       -> les regarder une fois, puis fixer NETTETE_MIN en tete de fichier")
    print("%s reflet sur le verre     %d image(s) ou plus de %.0f %% de la boite sature"
          % (verdict(not reflets), len(reflets), 100 * SPECULAIRE_PART))
    if reflets[:12]:
        print("       images concernees : %s%s"
              % (reflets[:12], " ..." if len(reflets) > 12 else ""))

    # --- couverture du plan : direction du regard = tete + pupille dans l'oeil
    print()
    print("COUVERTURE DU PLAN (direction du regard)")
    print("  colonnes = gauche -> droite, lignes = haut -> bas, chiffre = nb de poses")
    gx = (xs - xs.min()) / max(1e-9, np.ptp(xs))
    py = np.array([p[1] if p else 0.5 for p in pupilles], dtype=float)
    gy = (py - py.min()) / max(1e-9, np.ptp(py))
    grille = np.zeros((7, 12), dtype=int)
    for a, b in zip(gx, gy):
        grille[min(6, int(b * 7)), min(11, int(a * 12))] += 1
    for ligne in grille:
        print("   " + " ".join("%3d" % v if v else "  ." for v in ligne))
    trous = int((grille == 0).sum())
    print("  %d cases vides sur %d (%.0f %%)" % (trous, grille.size, 100 * trous / grille.size))

    json.dump({"suivi": suivi, "pupilles": pupilles, "speculaire": speculaire,
               "scores": scores, "nettetes": nettetes, "boite_oeil": list(boite)},
              open(os.path.join(DOSSIER, "releve.json"), "w"))
    print()
    print("qualite du suivi : score median %.2f (1 = calage parfait)" % float(np.median(scores)))
    print("relevé image par image : build/releve.json")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="commande", required=True)
    e = sous.add_parser("extraire"); e.add_argument("video")
    sous.add_parser("calibrer")
    m = sous.add_parser("mesurer")
    m.add_argument("--oeil", required=True, help="x,y,largeur,hauteur de la boîte de l'œil")
    args = p.parse_args()

    if args.commande == "extraire":
        extraire(args.video)
    elif args.commande == "calibrer":
        calibrer()
    else:
        mesurer(tuple(int(v) for v in args.oeil.split(",")))
