/* ------------------------------------------------------------------
   Le lézard suit le curseur.

   Les 25 poses sont des images réelles extraites de la vidéo source :
   une seule prise continue où la tête balaie le profil gauche jusqu'au
   profil droit. Chaque pose est associée à son angle de rotation, et
   on affiche celle qui correspond le mieux à la direction du curseur.
------------------------------------------------------------------ */

const COLS = 5;
const ROWS = 5;

/* Angle de la tête pour chaque case du sprite, de gauche à droite. */
const YAWS = [
  -90, -76, -60, -50, -42, -33, -25, -18, -12, -8, -6, -4, 0,
   7,  14,  20,  27,  34,  42,  50,  58,  66,  74,  82,  90
];
const CENTER = YAWS.indexOf(0);

/* Position de la tête dans l'image, en fraction du cadre. */
const HEAD_X = 0.607;
const HEAD_Y = 0.176;

const sprite = document.getElementById('lizard');
const character = document.querySelector('.character');
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

let yaw = 0, yawTarget = 0, restYaw = 0;
let leanX = 0, leanY = 0, leanXTarget = 0, leanYTarget = 0;
let shown = -1;
let lastPointer = 0;
let head = { x: 0, y: 0 };

/* ---------------------------------------------------------------- */

function measure() {
  const r = character.getBoundingClientRect();
  head.x = r.left + r.width * HEAD_X;
  head.y = r.top + r.height * HEAD_Y;
}

function show(index) {
  if (index === shown) return;
  shown = index;
  const col = index % COLS;
  const row = (index / COLS) | 0;
  sprite.style.backgroundPosition =
    `${(col * 100) / (COLS - 1)}% ${(row * 100) / (ROWS - 1)}%`;
}

function nearest(angle) {
  let best = 0, dist = Infinity;
  for (let i = 0; i < YAWS.length; i++) {
    const d = Math.abs(YAWS[i] - angle);
    if (d < dist) { dist = d; best = i; }
  }
  return best;
}

/* Le curseur au bord gauche de l'écran donne le profil gauche complet,
   au bord droit le profil droit : les deux extrêmes restent atteignables
   quelle que soit la largeur de la fenêtre. */
function aim(px, py) {
  const dx = px - head.x;
  const dy = py - head.y;
  const reach = dx < 0
    ? Math.max(200, head.x * 0.92)
    : Math.max(320, (window.innerWidth - head.x) * 0.78);

  const t = Math.max(-1, Math.min(1, dx / reach));
  yawTarget = restYaw = 90 * Math.sign(t) * Math.pow(Math.abs(t), 0.8);

  leanXTarget = Math.max(-16, Math.min(16, dx * 0.014));
  leanYTarget = Math.max(-12, Math.min(12, dy * 0.012));
  lastPointer = performance.now();
}

/* Curseur immobile : le lézard garde la direction du curseur mais
   respire légèrement, pour ne pas se figer comme une image. */
function idle(now) {
  const t = now / 1000;
  const drift = 9 * Math.sin(t * 0.37) + 4 * Math.sin(t * 0.83 + 1.7);
  yawTarget = Math.max(-90, Math.min(90, restYaw + drift));
  leanYTarget += (2.5 * Math.sin(t * 0.5) - leanYTarget) * 0.02;
}

let previous = performance.now();

function tick(now) {
  const dt = Math.min(0.05, (now - previous) / 1000);
  previous = now;

  if (!reduced.matches && now - lastPointer > 5000) idle(now);

  const ease = 1 - Math.exp(-9 * dt);
  yaw += (yawTarget - yaw) * ease;

  const slow = 1 - Math.exp(-5 * dt);
  leanX += (leanXTarget - leanX) * slow;
  leanY += (leanYTarget - leanY) * slow;

  show(nearest(yaw));
  character.style.setProperty('--lean-x', leanX.toFixed(2) + 'px');
  character.style.setProperty('--lean-y', leanY.toFixed(2) + 'px');
  character.style.setProperty('--lean-r', (yaw / 90 * 1.7).toFixed(2) + 'deg');

  requestAnimationFrame(tick);
}

/* ---------------------------------------------------------------- */

window.addEventListener('pointermove', (e) => aim(e.clientX, e.clientY), { passive: true });
window.addEventListener('pointerdown', (e) => aim(e.clientX, e.clientY), { passive: true });
window.addEventListener('resize', measure);
window.addEventListener('scroll', measure, { passive: true });

measure();
show(CENTER);
requestAnimationFrame(tick);

/* le cadre bouge pendant l'animation d'entrée : on relève sa position
   une fois qu'elle est terminée */
window.addEventListener('load', measure);
setTimeout(measure, 1400);

/* le sprite complet est décodé avant la première pose, pour éviter
   un clignotement au premier mouvement de souris */
const preload = new Image();
preload.src = 'assets/lezard.webp';
