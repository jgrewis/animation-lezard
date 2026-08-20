# Plan — Lézard qui suit le curseur, sur le fond d'origine

Projet : page d'arrivée « L'Animation de votre site web passe à un autre niveau »
Source : `Changements__Le_lézard_doit.mp4` (1280×720, 24 i/s, 240 images, 10 s)

---

## 1. Résumé des demandes

| # | Demande | Origine |
|---|---|---|
| D1 | Page d'arrivée ne contenant **que** la phrase « L'Animation de votre site web passe à un autre niveau » | msg 1 |
| D2 | Le lézard de la vidéo est **à gauche** | msg 1 |
| D3 | Il **suit le curseur**, avec les mouvements de la vidéo | msg 1 |
| D4 | Utiliser **strictement le fond d'origine** de la vidéo — plus aucun détourage, donc plus aucun écart de découpe visible | msg 2 |
| D5 | « Adapte le reste » : la mise en page suit ce choix de fond | msg 2 |
| D6 | Rendu **plus fluide** — il manquait des images | msg 3 |
| D7 | **Coordination verticale** du regard avec le pointeur | msg 3 |
| D8 | Appliquer le cadre de développement encadré | msg 4 |

---

## 2. Hors périmètre

- Aucun autre contenu que la phrase : ni logo, ni bouton, ni navigation, ni pied de page.
- Pas de mise en ligne, pas de dépôt Git : livraison en local.
- Pas de suivi du regard sur 2 axes réels (voir §3, arbitrage A1).
- Pas de nouvelle génération vidéo IA.

---

## 3. Décisions et arbitrages

### Tranché seul (mesures à l'appui)

**Dec-1 — Le balayage exploitable est celui des images 104 à 228.**
Vérifié image par image : une prise **continue et monotone**, profil gauche → face → profil droit. 125 poses, aucune coupure. Les autres passages de la vidéo (0–45 face, 46–63 face→gauche, 63–104 profil gauche tenu) ne sont pas réutilisables sans raccord visible.

**Dec-2 — La vidéo elle-même sert de source d'images, pilotée par `currentTime`.**
Mesuré dans le navigateur sur un banc d'essai : le `seek` piloté à chaque image tient **58,5 images/s** (tout-image-clé) et **60 i/s** (inter-codé). Le risque principal de cette approche est donc levé.

| | A — Vidéo tout-image-clé | B — Planche de sprites | C — Vidéo inter-codée |
|---|---|---|---|
| Poses disponibles | **125** | ~64 (limite de taille) | 125 |
| Poids | 2,0 Mo | 1,4 Mo pour 64 poses | 1,1 Mo |
| Fluidité | maximale | pas de 2,8° visible | maximale |
| Seek exact garanti | **oui, tout navigateur** | sans objet | dépend du navigateur |
| Réversibilité | totale (fichier isolé) | totale | totale |

→ **Option A retenue.** Le surcoût de 0,9 Mo achète l'exactitude du seek sur tout navigateur, et 125 poses au lieu de 64 — c'est exactement la demande D6.

**Dec-3 — Le fond de page prolonge le fond de la vidéo par un dégradé CSS calé sur ses propres couleurs**, plutôt que par une grande image de fond reconstruite. Les bords de la vidéo sont fondus au `mask-image`. Plus simple, sans image supplémentaire, et le raccord est **loin du personnage**.

**Dec-4 — Aucun bord de la vidéo n'est fondu près du personnage.**
Le bas de la vidéo est aligné sur le bas de la fenêtre (les pieds ne sont jamais estompés), le haut déborde hors écran. Seuls les bords gauche et droit sont fondus, à 27 % et 24 % du personnage.

**Dec-5 — La correspondance curseur → pose est calculée en « longueur d'arc perceptive ».**
La première version associait un angle estimé à l'œil à chaque image : c'est la cause de D7. Nouvelle méthode, objective : on mesure la différence réelle entre images consécutives, on en fait une somme cumulée, et le curseur parcourt cette somme linéairement. Le mouvement perçu devient donc **proportionnel au déplacement du curseur**, avec ancrage des trois repères (profil gauche / face / profil droit).

**Dec-6 — La planche `assets/lezard.webp` (963 Ko) est supprimée.** Elle devient morte avec l'abandon du détourage.

**Dec-7 — L'accent typographique passe du dégradé ambré au contraste de graisse.** Sur un fond orange, un accent ambré ne se lit plus.

### Arbitrage à trancher par le client

**A1 — Le suivi vertical du regard.**

*Ce qui est en jeu :* la demande D7. **La vidéo ne contient aucun mouvement de tête vertical indépendant.** Vérifié sur les 240 images : le lézard tourne la tête horizontalement, et son menton se lève *en conséquence* de la rotation (le tangage est lié au lacet, il n'est pas pilotable). Il n'existe aucune image de lui regardant en haut ou en bas de face.

| Option | Ce que ça donne | Coût |
|---|---|---|
| **1. Réponse par le corps** *(recommandée)* | Le regard reste horizontal ; la hauteur du curseur pilote une inclinaison 3D légère et un déplacement vertical du personnage. Cohérent, sans artefact. | Inclus |
| 2. Biaiser l'horizontale avec la verticale | Casse le suivi horizontal. **À écarter.** | — |
| 3. Nouvelle vidéo source | Vrai suivi 2 axes : il faut une vidéo où il regarde en haut et en bas, puis une grille de poses. | Nouvelle vidéo + refonte de la table de poses |

*Recommandation :* **option 1** maintenant, option 3 si le suivi 2 axes est vraiment nécessaire.

> **Réponse du client : option 1 — réponse par le corps.** Le regard reste horizontal ; la hauteur du curseur pilote une inclinaison 3D légère et un déplacement vertical du personnage.

**A2 — Poids du média.**
Arbitrage proposé : 2,0 Mo tout-image-clé (seek exact garanti partout) contre 1,1 Mo inter-codé (exactitude dépendante du navigateur).
> **Réponse du client : 2,0 Mo, tout-image-clé.**

---

## 4. Points de risque

| Risque | Dérisqué comment |
|---|---|
| Le `seek` vidéo saccade | **Levé** : banc d'essai navigateur, 58,5 i/s mesurées |
| Raccord visible entre la vidéo et le fond de page | Bords fondus au masque + dégradé calé sur les couleurs réelles échantillonnées dans la vidéo ; vérification visuelle en recette |
| Vidéo qui ne charge pas / JS en échec | Image d'affiche (`poster`) = pose de face. La page reste lisible et complète, sans le suivi |
| Contraste du texte sur fond orange | Mesuré : blanc sur `rgb(175,87,35)` = **4,99:1**, au-dessus du seuil AA. À revérifier à la position réelle du texte |
| Le personnage déborde ou est rogné sur petit écran | Composition dédiée en portrait : texte en haut, lézard en bas, pieds au ras du bord |
| Régression par rapport à la version livrée | La version actuelle fonctionne ; les fichiers sont réécrits, pas modifiés en place. Repli = revenir au commit… il n'y a pas de Git → **sauvegarde des 4 fichiers actuels dans `_precedent/` avant de commencer** |

---

## 5. Approche technique

### Fichiers

```
index.html          structure
styles.css          tokens + mise en page + fond
script.js           mesure de la scène, suivi du curseur, choix de la pose
assets/lezard.mp4   125 poses, tout-image-clé, 900×720          (nouveau)
assets/lezard.webp  image d'affiche, pose de face                (remplacé)
assets/poses.json   longueur d'arc cumulée par pose              (nouveau)
_precedent/         sauvegarde de la version actuelle            (nouveau)
```

### Tranches livrables

1. **T0 — Sauvegarde** de la version actuelle dans `_precedent/`.
2. **T1 — Fabrication des médias** : extraction 104→228, recadrage 900×720, encodage tout-image-clé à 25 i/s, calcul de la longueur d'arc, échantillonnage des couleurs de bord, image d'affiche.
3. **T2 — Squelette qui marche** : la vidéo affichée, le curseur choisit la pose. Rien d'autre. Valide l'assemblage de bout en bout.
4. **T3 — Fond et raccord** : dégradé de page, masque des bords, vérification qu'aucune jointure ne se voit.
5. **T4 — Typographie et mise en page**, tokens de `1.Regles.md`.
6. **T5 — Réponse verticale** (arbitrage A1) + comportement au repos.
7. **T6 — États et robustesse** : chargement, échec vidéo, `prefers-reduced-motion`, tactile.
8. **T7 — Recette** : checklist §6, puis usage humain réel.

---

## 6. Checklist

### Demandes

- [ ] D1 — La page ne contient que la phrase demandée, au mot près
- [ ] D2 — Le lézard est à gauche sur desktop
- [ ] D3 — La tête suit le curseur, du profil gauche au profil droit
- [ ] D4 — Aucun détourage : le fond visible autour du lézard est celui de la vidéo
- [ ] D5 — Le fond de page prolonge celui de la vidéo sans jointure visible
- [ ] D6 — 125 poses ; aucun saut perceptible en balayant lentement l'écran
- [ ] D7 — La hauteur du curseur produit une réponse visible et cohérente (selon A1)

### Référentiel — `1.Regles.md`

- [ ] Toutes les valeurs d'espacement sont des tokens de l'échelle 8pt
- [ ] Gouttières présentes à tous les paliers (16px mobile → 48px+ desktop)
- [ ] Interlignage du titre entre 1.1 et 1.3
- [ ] Grands espacements réduits sur mobile (`clamp()`)
- [ ] Aucune hauteur fixe sur un bloc de texte
- [ ] Zoom 200 % sans casse

### Référentiel — `2.BonnesPratiques.md`

- [ ] Reset moderne, `box-sizing`, `prefers-reduced-motion`
- [ ] Tokens CSS comme source unique de vérité (couleurs, espacements, plans)
- [ ] Grid/Flex + `gap` — aucune marge sur les enfants, aucun `float`
- [ ] Nommage BEM cohérent, spécificité plate, aucun `!important`, aucun ID de style
- [ ] Animation limitée à `transform` et `opacity`
- [ ] JS : module ES, `const`/`let`, aucune variable globale, aucun nombre magique non nommé
- [ ] Événements haute fréquence maîtrisés ; nettoyage des écouteurs
- [ ] Les trois états sont traités : chargement, échec, repli sans JS
- [ ] Aucun `console.log`, aucun code mort, aucun fichier orphelin
- [ ] `width`/`height` ou `aspect-ratio` sur tout média (CLS)

### Vérification humaine réelle

- [ ] Rendu vérifié à 375 px, 768 px, 1280 px et 1920 px — aucun défilement horizontal
- [ ] Le texte ne chevauche jamais le lézard, à aucune largeur
- [ ] Contraste du texte mesuré ≥ 4,5:1 à sa position réelle
- [ ] Aucune jointure visible entre la vidéo et le fond, sur les 4 côtés
- [ ] Le lézard atteint bien les deux profils extrêmes aux bords de l'écran
- [ ] Comportement au repos vérifié (curseur immobile)
- [ ] Comportement tactile vérifié (pas de curseur)
- [ ] `prefers-reduced-motion` vérifié
- [ ] Console : aucune erreur, aucune ressource 404
