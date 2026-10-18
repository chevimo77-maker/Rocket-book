# 🚀 ¡Rumbo a la Luna! — Libro interactivo

Libro interactivo de 14 páginas. Cada página es su propio archivo HTML autocontenido,
con flechas ← / → que llevan a la página anterior y siguiente. Diseñado para tablet
(1194×834) y escalado para laptop y móvil.

Online: https://chevimo77-maker.github.io/Rocket-book/

| # | Página | Archivo |
|---|--------|---------|
| 1 | Portada | `index.html` |
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

Navegación: flechas dentro de la página, teclado (← →) o deslizar horizontalmente en táctil.
Cada cambio de página tiene una transición (deslizar + fundido; solo fundido si el sistema pide menos movimiento).

## Estructura
- `index.html`, `pNN-*.html`: las 14 páginas (HTML plano, ~20 KB cada una).
- `assets/`: archivos compartidos (se descargan una sola vez): runtime, React, fuente, `book.css`, `book.js`
  (escalado, transiciones, teclado/gestos) y `noise/` (texturas de grano pre-renderizadas).
- `tools/build.py`: regenera las páginas y `assets/` desde `tools/source-book.html` (el export original):
  `python3 -I tools/build.py`. `tools/noise/*.html` son las fuentes de las texturas de `assets/noise/`
  (se renderizan con Chrome headless).

## Rendimiento
Antes cada página llevaba su propia copia comprimida de React, runtime y fuente (~175 KB) y reconstruía el
documento con JS al cargar. Ahora son ~20 KB por página + assets cacheados, la página se muestra ya
renderizada, y los 4 filtros `feTurbulence` a pantalla completa (muy costosos en tablets) se sustituyeron
por imágenes.

Fuente: Baloo 2 (SIL Open Font License 1.1), incluida dentro de cada archivo.
