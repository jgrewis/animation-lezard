# Cahier des charges — nouvelle matière source

À remettre à qui produira la vidéo. Ce document dit **ce qu'il faut tourner et
pourquoi**, avec les mesures qui le justifient et la recette à faire à la
livraison.

Objectif : un personnage **vivant qui suit le curseur du regard**, sur les deux
axes, y compris en biais. Pas un personnage qui fixe l'utilisateur.

---

## 1. Le vrai défaut de la prise actuelle

Ce n'est pas que les yeux bougent mal. **C'est qu'ils bougent en même temps que
la tête, et seulement comme elle.**

Relevé image par image sur les 125 poses, en suivant l'œil proche :

| Poses | Direction de la tête | Hauteur du regard |
|---|---|---|
| 0 – 13 | profil gauche | œil fermé ou dans l'ombre |
| 14 – 56 | gauche → face | pupille centrée |
| 57 – 74 | face → droite | la pupille monte |
| 75 – 95 | droite | regard franchement en haut, sclère blanche dessous |
| 96 – 124 | profil droit | pupille sortie du champ visible |

Autrement dit : **tête à droite ⇒ œil en haut, toujours.** Les deux mouvements
sont soudés. La prise parcourt une seule **diagonale** dans le plan
(direction de la tête × hauteur du regard).

Conséquence exacte dans la page livrée : le curseur ne pilote qu'un seul
paramètre, donc le regard monte quand l'utilisateur va à droite, même si son
curseur est en bas. Le mouvement n'est pas faux en soi — il est **mal indexé**.

> Une pose où l'œil regarde en haut est de la **bonne matière**. Elle doit
> simplement sortir quand le curseur est en haut.

### Ce qui manque, donc

Pas « du mouvement vertical » : **le reste du plan**. Il faut plusieurs
diagonales, ou mieux, un balayage complet des deux axes.

### Notre part

La table curseur → pose indexe les poses par leur **position dans le balayage**.
Il faut les indexer par **la direction qu'elles regardent**. Mesure qui le
montre : dans la zone qui sert à construire la table, **81 % du mouvement
mesuré venait des yeux** et non de la rotation de la tête — on croyait mesurer
une tête qui tourne, on mesurait un œil qui roule. Corrigé dès que la matière
sera saine.

---

## 2. Vidéo ou images ?

**Vidéo, en une seule prise continue.** Les images ne conviennent pas.

Ce dont le site a besoin n'est pas une animation mais une **collection de poses
parfaitement cohérentes entre elles** — la page ne lit jamais la vidéo, elle s'y
déplace, pose par pose. La vidéo garantit gratuitement ce qui est le plus dur à
obtenir autrement : d'une image à la suivante, seul bouge ce qui doit bouger.

Mesure sur la prise actuelle : le fond ne dérive que de **2,4/255** sur les 125
images. C'est cette stabilité qui rend le raccord du décor invisible. Une série
d'images générées une par une dérive à chaque rendu — peau, lunettes, lumière —
et chaque pas du suivi se met à scintiller.

Les images gardent un usage : **réparer une pose isolée**. Comme outil de
retouche, pas comme source.

---

## 3. Ce qu'il faut tourner

### Principe : couvrir le plan, pas une ligne

Le personnage doit regarder successivement **partout dans le champ** : haut
gauche, haut, haut droite, milieu gauche, milieu, milieu droite, bas gauche,
bas, bas droite — et tous les intermédiaires. Tête et yeux ensemble, comme
naturellement.

**La manière la plus sûre de l'obtenir : lui donner quelque chose à suivre.**
Un insecte qui vole lentement devant lui. Les générateurs rendent un
« il suit des yeux la mouche qui vole » bien mieux qu'une consigne d'angle. Et
le résultat est naturel par construction : la tête accompagne, les yeux
devancent, exactement ce qu'on cherche.

**Trajet demandé pour l'insecte** — un balayage en lignes, du haut vers le bas :

```
   ligne 1  ←──────────────────────────  (en haut)
   ligne 2  ──────────────────────────→
   ligne 3  ←──────────────────────────  (à hauteur des yeux)
   ligne 4  ──────────────────────────→
   ligne 5  ←──────────────────────────  (en bas)
```

Cinq lignes suffisent, sept sont confortables. Chaque ligne doit couvrir toute
l'amplitude horizontale, du profil gauche au profil droit, **à vitesse
constante**, sans pause et sans retour en arrière au milieu.

### Les segments, dans un seul fichier, sans couper la caméra

| # | Segment | Durée | Contenu |
|---|---|---|---|
| 1 | **Le balayage du plan** | 12 – 18 s | l'insecte parcourt les 5 à 7 lignes ci-dessus ; le lézard le suit des yeux et de la tête. Aucun clignement. |
| 2 | **Repos** | 3 s | le lézard revient de lui-même face caméra, regard droit devant, vers l'objectif |
| 3 | **Clignements** | 3 s | face caméra, deux ou trois clignements naturels, bien séparés |
| 4 | **Attente** | 3 s | face caméra : un coup de langue sur le museau, un léger mouvement d'attente |
| 5 | **Décor vide** | 2 s | le personnage sort du champ, caméra et lumière inchangées |

Une seule prise = une seule lumière, un seul fond, une seule identité. C'est ce
qui permet de composer les segments entre eux.

Les segments 2 à 4 servent **uniquement au repos** (voir §6) : c'est le seul
moment où le lézard regarde l'utilisateur.

Le segment 5 vaut de l'or : il donne la **vraie plaque de fond**, au lieu de
celle qu'il a fallu reconstruire en effaçant le personnage — c'est de cette
reconstruction que venaient les taches qu'on a dû noyer dans un flou.

### Combien d'images

| | Amplitude | Pas visé | Échantillons |
|---|---|---|---|
| Horizontal | profil à profil, ~130° | 2 à 3° | 45 à 65 par ligne |
| Vertical | ~50° utiles | 8 à 10° | 5 à 7 lignes |

Soit **250 à 450 poses**, c'est-à-dire 10 à 18 s à 25 i/s. Poids estimé du
média final : 3,5 à 7 Mo, contre 2 Mo aujourd'hui.

Optimisation possible si le poids gêne : **densifier la ligne médiane** (celle à
hauteur des yeux, de loin la plus utilisée) et espacer les lignes hautes et
basses. Le regard en biais extrême demande moins de finesse que le regard droit.

---

## 4. Contraintes non négociables

Dans l'ordre d'importance.

**1. Aucun clignement hors du segment 3.**
Le clignement est une matière à part, qu'on déclenche nous-mêmes après une
seconde d'immobilité — jamais pendant un mouvement.

**2. Chaque ligne du balayage couvre toute l'amplitude horizontale.**
Une ligne qui s'arrête à mi-course laisse un trou dans le plan : il y aura une
zone de l'écran sans pose correspondante.

**3. La pupille reste visible sur tout le balayage.**
C'est la limite qu'a franchie la prise actuelle à partir de la pose 100 : l'œil
roule si haut que la pupille sort du champ. Le regard peut aller haut, il ne
doit pas disparaître. Si le personnage doit lever les yeux au-delà, **c'est la
tête qui prend le relais**.

**4. Caméra fixe, lumière fixe, fond fixe.**
Aucun zoom, aucun travelling, aucun recadrage, aucune variation d'éclairage.
Le personnage ne se déplace pas dans le cadre : seules la tête et les yeux
bougent. Tolérance : **2 px de translation** sur toute la prise.

**5. Vitesse constante.**
Sur la prise actuelle, 37 % du mouvement tient dans les 20 premières poses et
2 % dans les 20 suivantes ; il a fallu compenser par calcul. Une vitesse
régulière rend la correspondance curseur → pose exacte par construction.

**6. Rien d'autre ne bouge.**
Pas de respiration marquée, pas de balancement du corps, pas de mouvement de
queue ni de main pendant le balayage. Tout ce qui bouge en plus devient un
tremblement quand on saute d'une pose à l'autre.

**7. Pas de reflet saturé sur les verres.**
Un reflet spéculaire qui balaie le verre pendant la rotation masque l'œil. Si
l'éclairage ne peut pas l'éviter : verres antireflet, ou version sans lunettes.

**8. La tête doit être grande dans le cadre.**
Aujourd'hui l'œil fait environ 45 px de large. Pour lire une direction de regard
au degré près, il en faut **60 au minimum, 90 idéalement** : cadrage plus serré,
ou livraison en 1920 × 1080 au lieu de 1280 × 720.

---

## 5. Livraison

- **Suite d'images PNG**, ou master sans perte (ProRes, FFV1). À défaut, H.264
  en **CRF 16 ou mieux**, sans redimensionnement.
- **24 ou 25 images par seconde**, constant, sans image dupliquée.
- Aucun montage, aucun fondu, aucune correction colorimétrique après coup.
- Si le fichier est encodé : **balises de couleur présentes** (primaires,
  courbe, matrice, plage). Sans elles, chaque logiciel décode à sa façon — c'est
  ce qui a fait apparaître le cadre vidéo comme un rectangle plus clair sur le
  fond, et il a fallu le diagnostiquer au pixel.

---

## 6. Le comportement au repos, à produire aussi

Séquence voulue, à jouer avec les segments 2 à 4 :

1. **1 seconde sans mouvement du curseur.**
2. Le lézard **revient en position neutre** et regarde droit devant lui, vers
   l'utilisateur. C'est le seul moment où il le fixe.
3. Il **cligne des yeux**, et de temps en temps passe la langue sur son museau,
   en signe d'attente.
4. **Dès que le curseur rebouge, il le suit immédiatement** — aucun retard,
   aucun amorti à la reprise.

C'est cette séquence qui fait la différence entre une animation et une présence.

---

## 7. Recette à la livraison

À faire **avant** de rien intégrer. Chaque point est mesurable.

| Contrôle | Méthode | Seuil |
|---|---|---|
| Pupille visible sur 100 % du segment 1 | planche contact de la bande des yeux, image par image | aucune exception |
| Aucun clignement hors segment 3 | même planche | aucune exception |
| Couverture du plan | position de la pupille dans l'œil, relevée sur chaque image, portée sur un nuage de points | aucun trou de plus de 5 % de la surface |
| Chaque ligne va d'un profil à l'autre | direction de la tête, début et fin de ligne | amplitude complète |
| Dérive du fond | écart moyen première/dernière image, hors personnage | ≤ 3/255 |
| Translation du personnage | position du museau, première et dernière image | ≤ 2 px |
| Régularité du balayage | écart entre pas consécutifs | ≤ 2× la médiane |
| Reflet sur les verres | luminance maximale dans la zone du verre | < 240/255 |

La **planche contact de la bande des yeux** est l'outil décisif : toutes les
poses en vignettes sur une seule image, et le défaut saute aux yeux en trois
secondes. C'est elle qui a révélé le problème actuel — elle aurait dû être faite
**avant** de construire quoi que ce soit. Exemples dans [`preuves/`](preuves).

---

## 8. Ce qui change côté code, une fois la matière livrée

- **Les poses sont indexées par la direction qu'elles regardent**, plus par leur
  rang dans le balayage. Pour chaque image on relève la direction de la tête et
  la position de la pupille dans l'œil ; la somme des deux donne la direction du
  regard. La page cherche ensuite la pose dont la direction pointe le plus près
  du curseur — sur les deux axes, croisements compris.
- **Fondu entre les deux poses voisines** au lieu d'un saut : le décodeur tient
  **219 poses par seconde** (4,2 ms par déplacement, mesuré en ligne), il reste
  donc toute la marge nécessaire pour afficher deux poses mélangées.
- **Ressort amorti** à la place du lissage exponentiel actuel, et **reprise
  instantanée** à la sortie du repos.
- **Zone de mesure hors des yeux** pour tout ce qui concerne la tête.
- **Micro-saccades** au repos : l'œil réel ne glisse pas, il saute.
