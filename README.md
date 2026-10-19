# 🚀 ¡Rumbo a la Luna! — Libro interactivo

Libro interactivo de 14 páginas. Cada página es su propio archivo HTML autocontenido,
con flechas ← / → que llevan a la página anterior y siguiente. Diseñado para tablet
(1194×834) y escalado para laptop y móvil.

Online: https://chevimo77-maker.github.io/Rocket-book/

| # | Página | Archivo |
|---|--------|---------|
| 1 | Portada | `p01-cover.html` |
| 2 | Entrenamiento | `p02-training.html` |
| 3 | A vestirse | `p03-suit-up.html` |
| 4 | A la plataforma | `p04-rollout.html` |
| 5 | Combustible | `p05-fuel.html` |
| 6 | A bordo | `p06-board.html` |
| 7 | Cuenta regresiva | `p07-countdown.html` |
| 8 | Despegue | `p08-liftoff.html` |
| 9 | El propulsor vuelve | `p09-booster.html` |
| 10 | Bomba de gasolina espacial | `p10-refuel.html` |
| 11 | Viaje a la Luna | `p11-journey.html` |
| 12 | Aterrizaje | `p12-landing.html` |
| 13 | Paseo lunar | `p13-moonwalk.html` |
| 14 | Regreso a casa | `p14-home.html` |

Pantalla completa: botón arriba a la derecha (no aparece en iPhone, donde Safari no lo permite).

Navegación: flechas dentro de la página, teclado (← →) o deslizar horizontalmente en táctil.
Cada cambio de página tiene una transición (deslizar + fundido; solo fundido si el sistema pide menos movimiento).

## Estructura
- `index.html`: el lector. Muestra las páginas en un marco y tiene el botón de pantalla completa (así la
  pantalla completa se mantiene al pasar de página). La URL guarda la página: `index.html#p07-countdown.html`.
  Si se abre una página suelta, redirige al lector (`?solo` lo evita, lo usa el benchmark).
- `pNN-*.html`: las 14 páginas (HTML plano, ~20 KB cada una).
- `manifest.webmanifest`: en iPad/Android, "Añadir a pantalla de inicio" abre el libro a pantalla completa.
- `assets/`: archivos compartidos (se descargan una sola vez): runtime, React, fuente, `book.css`, `book.js`
  (escalado, transiciones, teclado/gestos).
- `tools/build.py`: regenera las páginas y `assets/` desde `tools/source-book.html` (el export original):
  `python3 -I tools/build.py`.
- `tools/restyle.py`: el diseño estilo SeaBeans (plano, contorno azul marino grueso, colores pastel). Paleta,
  contornos y tarjetas para todas las páginas, y los personajes redibujados: Ana y Leo (cuerpo entero y caras en
  ventanas), el cohete gordito con cara, la Luna, el propulsor de la página 9. Las bocas pequeñas que quedan se
  cambian por sonrisas abiertas.
- `tools/shots.mjs`: captura cada página después de cada toque (`node tools/shots.mjs /tmp/out p07-countdown`),
  para revisar que las animaciones encajan con los dibujos.

## Rendimiento
Antes cada página llevaba su propia copia comprimida de React, runtime y fuente (~175 KB) y reconstruía el
documento con JS al cargar. Ahora son ~20 KB por página + assets cacheados, la página se muestra ya
renderizada, y los 4 filtros `feTurbulence` a pantalla completa (muy costosos en tablets) se sustituyeron
por imágenes.

Animaciones: el filtro SVG `shade` de los personajes se recalculaba en cada fotograma (ruido + desplazamiento
+ desenfoque), y las texturas usaban `mix-blend-mode`, que obliga a mezclar toda la pantalla por fotograma.
Con el rediseño ya no hay filtros ni texturas: el contorno es un trazo normal.

Benchmark: `node tools/bench.mjs [throttle] [páginas...]` abre Chrome headless con CPU ralentizada y
render por software a 2x, toca la escena varias veces y mide fps. Con CPU 6x más lenta: antes 16–43 fps en
varias páginas, ahora 60 fps en las 14.

Fuente: Baloo 2 (SIL Open Font License 1.1), en `assets/baloo2-latin.woff2` (licencia en `assets/OFL-Baloo2.txt`).
