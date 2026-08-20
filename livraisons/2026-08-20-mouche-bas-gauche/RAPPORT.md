# Rapport — préparation de la prise `mouche-bas-gauche`

1. Fichier reçu : `la_mouche_pars_du_bas_à_gauche.mp4` — 2026-08-20 — mot-clef `mouche-bas-gauche`

   Note d'aiguillage (hors mesures) : un second fichier joint,
   `Changements__Le_lézard_doit (1).mp4`, avait une empreinte MD5 identique à
   `Changements__Le_lézard_doit.mp4` déjà présent à la racine du dépôt (celui
   qui a servi à fabriquer la prise actuelle, 125 poses). Confirmé avec
   l'expéditeur : ce doublon est ignoré, seul `la_mouche_pars_du_bas_à_gauche.mp4`
   est traité ici.

2. Fiche technique (`PROBE.txt`) :

   ```
   width=1280
   height=720
   pix_fmt=yuv420p
   color_range=unknown
   color_space=unknown
   color_transfer=unknown
   color_primaires=unknown
   r_frame_rate=24/1
   nb_frames=240
   ```

   Balises de couleur manquantes : `color_space`, `color_range`, `color_transfer`
   et `color_primaries` valent tous `unknown`.

3. 240 images extraites, correspond à `nb_frames` (240). Aucun écart.

4. Sortie brute de l'étape 4 :

   ```
   NOUVELLE PRISE
     0001.png {'taille': (1280, 720), 'fond_coins_RVB': [118.5, 62.8, 33.8], 'perso_largeur_px': 939, 'perso_hauteur_px': 719, 'perso_centre_x': 808}
     0121.png {'taille': (1280, 720), 'fond_coins_RVB': [118.2, 62.5, 33.8], 'perso_largeur_px': 1235, 'perso_hauteur_px': 719, 'perso_centre_x': 776}
     0240.png {'taille': (1280, 720), 'fond_coins_RVB': [103.2, 85.3, 66.8], 'perso_largeur_px': 1279, 'perso_hauteur_px': 719, 'perso_centre_x': 623}
   REFERENCE (pose de face de la prise actuelle)
     pose-de-face.png {'taille': (900, 720), 'fond_coins_RVB': [167.6, 82.3, 33.1], 'perso_largeur_px': 705, 'perso_hauteur_px': 683, 'perso_centre_x': 518}
   ```

5. Boîte de l'œil retenue : `520,50,170,156` (coin haut-gauche 520,50 — largeur
   170, hauteur 156), sur une image de 1280 px de large — œil gauche du
   personnage, le plus visible et le plus dégagé des reflets de lunettes.

   Sortie brute de l'étape 5 :

   ```
   ================================================================
   RECETTE DE LA MATIERE — 240 images
   ================================================================
   NON  derive du fond          36.39 /255   (seuil 3)
        amplitude horizontale     267 px      (course de l'oeil suivi)
        amplitude verticale        48 px
   NON  regularite du balayage  pas median 0.0 px, p90 7.2, max 19.2  (rapport 0.0)
   OK   pupille visible         0 image(s) sans pupille
   OK   nettete de la pupille   mediane 0.86, minimum 0.65
          les 10 images les plus faibles : 201 (0.72), 202 (0.74), 203 (0.71), 204 (0.71), 205 (0.73), 229 (0.72), 230 (0.71), 231 (0.65), 232 (0.67), 233 (0.71)
          -> les regarder une fois, puis fixer NETTETE_MIN en tete de fichier
   OK   reflet sur le verre     0 image(s) ou plus de 10 % de la boite sature

   COUVERTURE DU PLAN (direction du regard)
     colonnes = gauche -> droite, lignes = haut -> bas, chiffre = nb de poses
       44   1   1   .   .   .   .   .   .   .   .   .
        7   3   .   1   .   .   .   .   .   .   .   2
        .   .   1   .   1   .   .   .   .   7   .  18
        .   .   1   2   .   1   .   .   .  10   1   6
        .   .   .   .   2   3   2   2   .   .   8   1
        .   .   .   .   .  46   .   3  12   .   4   1
        .   .   .   .   .   .   .   .  28   9  12   .
     53 cases vides sur 84 (63 %)

   qualite du suivi : score median 0.86 (1 = calage parfait)
   relevé image par image : build/releve.json
   ```

   Score médian 0,86 — au-dessus du seuil de 0,6, pas de nouvel essai nécessaire.

6. Ce qui a échoué ou surpris :
   - Le fond du dossier ne correspond pas aux mesures de la prise actuelle :
     `fond_coins_RVB` va de (118.5, 62.8, 33.8) à (103.2, 85.3, 66.8) sur cette
     prise, contre (167.6, 82.3, 33.1) sur `reference/pose-de-face.png`. Le
     contrôle « dérive du fond » de l'étape 5 échoue aussi (36,39/255, seuil 3).
   - `perso_largeur_px` grimpe jusqu'à 1279 px (quasi toute la largeur de
     l'image, 1280 px) en fin de prise, contre 705 px sur la référence (image
     de 900 px de large) — la silhouette détectée par le seuil de couleur
     couvre une part très différente du cadre.
   - La couverture du plan de regard est très inégale : 63 % des cases sont
     vides, avec deux concentrations fortes (44 poses dans une case en haut à
     gauche, 46 au centre-bas).
   - Aucune balise de couleur dans le fichier source (point 2).

   Aucun chiffre n'est interprété ici — ces écarts sont rapportés tels quels
   pour décision.
