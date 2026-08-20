/* ==================================================================
   Le lézard suit le curseur.

   Ce ne sont pas des dessins : ce sont ses propres images. La vidéo
   assets/lezard.mp4 contient les 125 poses d'un même balayage continu,
   du profil gauche au profil droit, toutes en images-clés. Déplacer
   currentTime revient donc à choisir une pose, et rien d'autre.

   Le fichier ne crée aucune variable globale : tout tient dans la
   fonction ci-dessous. Un module ES aurait été refusé par le navigateur
   à l'ouverture directe du fichier (file://), et la page doit aussi
   marcher par double-clic.
================================================================== */

(function () {
  'use strict';

  /* Table curseur -> pose, calculée en longueur d'arc perceptive de la
     tête seule (build/arc.py). 401 entrées, de u = -1 au bord gauche de
     l'écran à u = +1 au bord droit, u = 0 à l'aplomb du lézard.
     Le mouvement perçu est ainsi proportionnel au déplacement du curseur. */
  var LUT = [
  0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6,
  6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10,
  10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
  12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14,
  14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 17, 17, 17, 18, 18, 18,
  18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 35, 37, 38,
  39, 40, 41, 42, 43, 44, 44, 45, 46, 47, 47, 48, 48, 49, 49, 49, 50, 50, 51, 51, 51, 52,
  52, 52, 52, 53, 53, 53, 54, 54, 54, 55, 55, 55, 56, 56, 56, 57, 57, 57, 58, 58, 58, 58,
  59, 59, 59, 60, 60, 60, 61, 61, 61, 61, 62, 62, 62, 63, 63, 63, 64, 64, 64, 65, 65, 65,
  66, 66, 66, 67, 67, 68, 68, 68, 69, 69, 69, 70, 70, 70, 71, 71, 71, 71, 72, 72, 72, 73,
  73, 73, 74, 74, 74, 75, 75, 75, 76, 76, 76, 77, 77, 78, 78, 79, 80, 80, 81, 82, 83, 84,
  85, 86, 88, 90, 91, 92, 92, 93, 93, 94, 94, 94, 95, 95, 95, 95, 96, 96, 96, 96, 97, 97,
  97, 97, 97, 97, 98, 98, 98, 98, 98, 99, 99, 99, 99, 99, 100, 100, 100, 100, 100, 101, 101,
  101, 101, 102, 102, 102, 103, 103, 103, 104, 104, 104, 105, 105, 106, 106, 107, 108, 108,
  109, 110, 111, 113, 114, 116, 118, 119, 120, 120, 121, 121, 121, 122, 122, 122, 122, 123,
  123, 123, 123, 124, 124, 124
  ];

  var IMAGES_PAR_SECONDE = 25;

  /* entre les deux yeux, en fraction du cadre vidéo : c'est de ce point
     que part la direction du regard (relevé sur la pose de face) */
  var TETE_X = 0.603;
  var TETE_Y = 0.146;

  /* portées minimales : le profil complet reste atteignable même dans une
     fenêtre étroite, sans devenir nerveux dans une fenêtre large */
  var PORTEE_GAUCHE_MIN = 200;
  var PORTEE_DROITE_MIN = 320;
  var PART_GAUCHE = 0.92;
  var PART_DROITE = 0.78;
  var PART_VERTICALE = 0.42;
  var PORTEE_VERTICALE_MIN = 240;

  /* réponse verticale : le regard reste horizontal, c'est le corps qui
     répond — la vidéo ne contient aucun mouvement de tête vertical */
  var POUSSEE = 0.02;      /* en fraction de la hauteur du cadre */
  var BASCULE = 1.2;       /* degrés */

  var SOUPLESSE_TETE = 11; /* nervosité du suivi : 11 = vif, 4 = paresseux */
  var SOUPLESSE_CORPS = 5;
  var ATTENTE_REPOS = 4000;

  var scene = document.querySelector('.scene');
  var plaque = document.querySelector('.scene__plaque');
  var cadre = document.querySelector('.scene__cadre');
  var video = document.getElementById('poses');
  if (!scene || !plaque || !cadre || !video) return;

  var sobre = window.matchMedia('(prefers-reduced-motion: reduce)');
  var tactile = window.matchMedia('(pointer: coarse)');

  var u = 0, uVise = 0, uRepos = 0;
  var w = 0, wVise = 0;
  var tete = { x: 0, y: 0 };
  var hauteurCadre = 0;
  var posee = -1;
  var prete = false;
  var dernierGeste = tactile.matches ? -Infinity : 0;

  function mesurer() {
    var r = cadre.getBoundingClientRect();
    tete.x = r.left + r.width * TETE_X;
    tete.y = r.top + r.height * TETE_Y;
    hauteurCadre = r.height;
  }

  function viser(px, py) {
    var dx = px - tete.x;
    var dy = py - tete.y;
    var portee = dx < 0
      ? Math.max(PORTEE_GAUCHE_MIN, tete.x * PART_GAUCHE)
      : Math.max(PORTEE_DROITE_MIN, (window.innerWidth - tete.x) * PART_DROITE);
    var porteeV = Math.max(PORTEE_VERTICALE_MIN, window.innerHeight * PART_VERTICALE);

    uVise = uRepos = Math.max(-1, Math.min(1, dx / portee));
    wVise = Math.max(-1, Math.min(1, dy / porteeV));
    dernierGeste = performance.now();
  }

  /* Curseur immobile, ou écran tactile : le lézard continue de regarder
     autour de lui, doucement, plutôt que de se figer comme une image. */
  function repos(maintenant) {
    var t = maintenant / 1000;
    var derive = 0.22 * Math.sin(t * 0.31) + 0.09 * Math.sin(t * 0.74 + 1.7);
    uVise = Math.max(-1, Math.min(1, uRepos + derive));
    wVise += (0.18 * Math.sin(t * 0.46) - wVise) * 0.02;
  }

  function poser(index) {
    if (index === posee) return;
    posee = index;
    video.currentTime = (index + 0.5) / IMAGES_PAR_SECONDE;
  }

  var precedent = performance.now();

  function boucle(maintenant) {
    var dt = Math.min(0.05, (maintenant - precedent) / 1000);
    precedent = maintenant;

    if (!sobre.matches && maintenant - dernierGeste > ATTENTE_REPOS) repos(maintenant);

    u += (uVise - u) * (1 - Math.exp(-SOUPLESSE_TETE * dt));
    w += (wVise - w) * (1 - Math.exp(-SOUPLESSE_CORPS * dt));

    if (prete) poser(LUT[Math.round((u + 1) / 2 * (LUT.length - 1))]);

    if (!sobre.matches) {
      plaque.style.setProperty('--pousse-y', (w * POUSSEE * hauteurCadre).toFixed(2) + 'px');
      plaque.style.setProperty('--bascule', (-w * BASCULE).toFixed(2) + 'deg');
    }

    requestAnimationFrame(boucle);
  }

  /* Trois états à tenir : la vidéo se charge, la vidéo échoue, la vidéo
     se charge mais refuse le déplacement. Ce dernier cas n'est pas théorique :
     un serveur qui ignore l'en-tête Range rend la vidéo non déplaçable, et
     tout currentTime retombe à zéro. Dans les deux cas de panne, la pose de
     face reste affichée et la page garde son sens, sans le suivi. */
  var ECOUTES = ['loadeddata', 'progress', 'canplaythrough'];

  function oublier() {
    for (var i = 0; i < ECOUTES.length; i++) video.removeEventListener(ECOUTES[i], surveiller);
  }

  function replier() {
    prete = false;
    oublier();
    scene.classList.add('scene--repli');
  }

  function deplacable() {
    return video.seekable.length > 0 && video.seekable.end(0) > 0;
  }

  /* La vidéo n'est pas toujours déplaçable dès la première image reçue :
     on ne conclut à la panne qu'une fois le fichier entièrement chargé. */
  function surveiller() {
    if (deplacable()) {
      oublier();
      mesurer();
      prete = true;
      poser(LUT[Math.round((u + 1) / 2 * (LUT.length - 1))]);
      video.addEventListener('seeked', function () {
        scene.classList.add('scene--prete');
      }, { once: true });
      return;
    }
    if (video.readyState >= 4) replier();
  }

  for (var i = 0; i < ECOUTES.length; i++) video.addEventListener(ECOUTES[i], surveiller);
  video.addEventListener('error', replier, { once: true });
  if (video.readyState >= 2) surveiller();

  window.addEventListener('pointermove', function (e) { viser(e.clientX, e.clientY); }, { passive: true });
  window.addEventListener('pointerdown', function (e) { viser(e.clientX, e.clientY); }, { passive: true });
  window.addEventListener('resize', mesurer, { passive: true });
  window.addEventListener('load', mesurer);

  mesurer();
  requestAnimationFrame(boucle);
})();
