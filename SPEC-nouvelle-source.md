# Cahier des charges — nouvelle matière source

À remettre à qui produira la vidéo. Ce document dit **ce qu'il faut tourner et
pourquoi**, avec les mesures qui le justifient et la recette à faire à la
livraison.

---

## 1. Pourquoi refaire la matière

La vidéo actuelle donne 125 poses. **43 seulement sont utilisables.** Le reste
n'a pas de regard lisible. Relevé image par image sur les 125 :

| Poses | État de l'œil | Part |
|---|---|---|
| 0 – 5 | fermé ou dans l'ombre | 5 % |
| 6 – 13 | en train de s'ouvrir | 6 % |
| **14 – 56** | **ouvert, iris et pupille lisibles** | **34 %** |
| 57 – 74 | la pupille remonte, l'œil se voile | 14 % |
| 75 – 124 | dôme crème derrière le verre : ni iris ni pupille | 40 % |

Les planches contact qui servent de preuve sont dans [`preuves/`](preuves) :
les 125 poses en bande des yeux, et deux agrandissements sur les zones de
bascule (poses 45 à 74, puis 75 à 104).

Vérifié en agrandissement : sur la fin du balayage ce **n'est pas un reflet sur
la lunette** — le dôme pâle est derrière le verre, la monture et son reflet
propre sont visibles par-dessus. C'est la paupière, ou le globe retourné.

Conséquence directe dans la page livrée : **toute la moitié droite de l'écran
envoie le lézard dans des poses où il ne regarde plus personne.** Et le
clignement du bord gauche apparaît en plein mouvement, ce qui n'a aucun sens.

### Le défaut se propage dans notre table

La table curseur → pose est calculée sur « ce qui bouge » d'une image à l'autre,
dans une zone qui **contenait les yeux**. Résultat mesuré :

- **81 % du mouvement mesuré vient de la seule zone des yeux**, pas de la
  rotation de la tête ;
- les images de clignement pèsent jusqu'à **3,8 fois** la médiane ;
- la table leur alloue donc jusqu'à **3,7 % de la largeur de l'écran chacune**,
  contre 0,8 % pour une pose moyenne — soit **4,6 fois trop**.

Autrement dit, non seulement le clignement est là, mais on s'attarde dessus.
C'est une erreur de méthode de notre côté, corrigée dès que la matière sera
saine (zone de mesure restreinte au crâne et au museau, yeux exclus).

---

## 2. Vidéo ou images ?

**Vidéo, en une seule prise continue.** Les images seules ne conviennent pas.

La raison est simple : ce dont le site a besoin, ce n'est pas d'une animation,
c'est d'une **collection de poses parfaitement cohérentes entre elles**. La page
ne lit jamais la vidéo — elle s'y déplace pose par pose. Une vidéo n'est ici
qu'un conteneur d'images, mais un conteneur qui garantit gratuitement ce qui est
le plus difficile à obtenir autrement : **d'une image à la suivante, seul bouge
ce qui doit bouger**.

Mesure à l'appui sur la prise actuelle : le fond ne dérive que de **2,4/255**
entre la première et la dernière des 125 images. C'est cette stabilité qui
permet de reconstruire une plaque de fond unique et de ne rien voir du raccord.
Une série d'images générées une par une dérive au contraire à chaque rendu —
texture de peau, forme des lunettes, lumière — et chaque pas du suivi se met à
scintiller.

Les images gardent un usage : **réparer une pose isolée** (repeindre un œil sur
une image précise). Comme outil de retouche, pas comme source.

### Une seule prise, cinq segments, dans cet ordre

Tout dans **un seul fichier**, sans couper la caméra ni retoucher la lumière
entre les segments. C'est ce qui garantit que les cinq segments se composent
entre eux.

| # | Segment | Durée | Ce qui doit s'y passer |
|---|---|---|---|
| 1 | **Regard vertical** | 3 s | Tête immobile, face caméra. Les yeux seuls montent au plafond puis descendent au sol, lentement, sans à-coup. |
| 2 | **Regard horizontal** | 3 s | Tête immobile, face caméra. Les yeux seuls balaient de gauche à droite. |
| 3 | **Clignements** | 3 s | Tête immobile, face caméra. Deux ou trois clignements naturels, bien séparés. |
| 4 | **Balayage de la tête** | 10 s | La tête tourne du profil gauche au profil droit, **à vitesse constante**, sans pause, sans retour. **Les yeux restent grands ouverts et fixent l'objectif pendant tout le mouvement.** Aucun clignement. |
| 5 | **Décor vide** | 2 s | Le personnage sort du champ. Caméra et lumière inchangées. |

Le segment 5 vaut de l'or : il nous donne la **vraie plaque de fond**, au lieu de
celle qu'on a dû reconstruire en effaçant le personnage — c'est de cette
reconstruction que venaient les taches qu'il a fallu noyer dans un flou.

Le segment 4 seul suffirait à refaire le site tel quel. Ce sont les segments 1
à 3 qui débloquent ce qui manque aujourd'hui : le suivi vertical par les yeux et
le clignement au repos.

---

## 3. Contraintes non négociables

Dans l'ordre d'importance. Les trois premières décident du succès.

**1. Les yeux fixent l'objectif pendant tout le segment 4.**
C'est la contrainte qui a été manquée la dernière fois, et elle coûte 66 % de la
matière. À formuler explicitement à la génération, et à **vérifier image par
image** à la livraison, pas au visionnage.

**2. Aucun clignement dans les segments 1, 2, 4 et 5.**
Le clignement est une matière à part (segment 3), qu'on jouera nous-mêmes,
uniquement après une seconde d'immobilité du curseur — jamais pendant un
mouvement.

**3. Caméra fixe, lumière fixe, fond fixe.**
Aucun zoom, aucun travelling, aucun recadrage, aucune variation d'éclairage
entre le début et la fin. Le personnage ne doit pas se déplacer dans le cadre :
seule sa tête tourne. Tolérance : **2 px de translation** sur toute la prise.

**4. Vitesse constante sur le balayage.**
Sur la prise actuelle, 37 % du mouvement tient dans les 20 premières poses et
2 % dans les 20 suivantes. Il a fallu compenser par calcul. Un balayage à
vitesse régulière rend la correspondance curseur → pose exacte par construction.

**5. Rien d'autre ne bouge.**
Pas de respiration marquée, pas de balancement du corps, pas de mouvement de
queue ni de main pendant le balayage. Tout ce qui bouge en plus de la tête
devient un tremblement quand on saute d'une pose à l'autre.

**6. Pas de reflet saturé sur les verres.**
Les lunettes sont un risque : un reflet spéculaire qui balaie le verre pendant
la rotation masque l'œil. Si l'éclairage ne peut pas l'éviter, il vaut mieux
**une version sans lunettes**, ou des verres traités antireflet.

**7. La tête doit être grande dans le cadre.**
Aujourd'hui l'œil fait environ 45 px de large. Pour composer un regard net, il
en faut **au moins 60, idéalement 90**. Soit en cadrant plus serré, soit en
livrant en 1920 × 1080 au lieu de 1280 × 720.

---

## 4. Livraison

- **Une suite d'images PNG**, ou un master sans perte (ProRes, FFV1). À défaut,
  H.264 en **CRF 16 ou mieux**, sans redimensionnement.
- **24 ou 25 images par seconde**, constant, sans images dupliquées.
- Aucun montage, aucun fondu, aucune correction colorimétrique après coup.
- Si le fichier est encodé : **les balises de couleur doivent être présentes**
  (primaires, courbe, matrice, plage). Sans elles, chaque logiciel décode à sa
  façon — c'est ce qui a fait apparaître le cadre vidéo comme un rectangle plus
  clair sur le fond, et il a fallu le diagnostiquer au pixel. À défaut on
  réétiquette nous-mêmes, mais autant l'éviter.

---

## 5. Recette à la livraison

À faire **avant** de rien intégrer. Chaque point est mesurable.

| Contrôle | Méthode | Seuil |
|---|---|---|
| Pupille visible sur 100 % des images du segment 4 | planche contact de la bande des yeux, image par image | aucune exception |
| Aucun clignement hors segment 3 | même planche | aucune exception |
| Dérive du fond | écart moyen entre la première et la dernière image, hors personnage | ≤ 3/255 |
| Translation du personnage | position du museau, première et dernière image | ≤ 2 px |
| Rotation monotone | écart entre les deux yeux, image par image | strictement croissant puis décroissant, sans retour |
| Régularité du balayage | même mesure, écart entre pas consécutifs | ≤ 2× la médiane |
| Reflet sur les verres | luminance maximale dans la zone du verre | < 240/255 |

La planche contact de la bande des yeux est l'outil décisif : 125 vignettes sur
une seule image, et le défaut saute aux yeux en trois secondes. C'est elle qui a
révélé le problème actuel — elle aurait dû être faite **avant** de construire
quoi que ce soit.

---

## 6. Ce que la nouvelle matière permettra

- **Suivi vertical réel par les yeux** : la pupille suit la hauteur du curseur,
  au lieu de l'inclinaison du corps qui la remplace aujourd'hui.
- **Suivi à deux axes** : direction de la tête donnée par X, direction du regard
  donnée par X et Y — c'est ce qui produit l'impression qu'il vous regarde
  vraiment, et non qu'il tourne la tête.
- **Clignement maîtrisé** : jamais en mouvement, uniquement après une seconde
  d'immobilité, avec une reprise naturelle.
- **Micro-saccades au repos** : l'œil réel ne glisse pas, il saute. C'est ce
  détail qui fait la différence entre « ça suit » et « il me regarde ».
- **Mouvement continu** : le décodeur tient **219 poses par seconde** (4,2 ms par
  déplacement, mesuré en ligne). Il reste donc largement de quoi fondre deux
  poses voisines l'une dans l'autre et supprimer le dernier escalier perceptible.
  Le banc d'essai initial annonçait 58,5 : la marge est trois fois plus grande
  qu'on ne le croyait.

Côté code, trois corrections déjà identifiées : zone de mesure de la table
**hors des yeux**, ressort amorti au lieu du lissage exponentiel actuel, et
composition du regard en surcouche du cadre vidéo.
