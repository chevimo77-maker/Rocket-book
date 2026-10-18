# 🚀 ¡Rumbo a la Luna! — Libro interactivo

Interactive children's book. `index.html` is the book shell (page navigator + viewer);
each book page is a self-contained HTML file in `pages/`.

## Pages
| # | Page | File |
|---|------|------|
| 7 | Cuenta regresiva | `pages/07-cuenta-regresiva.html` |

## Adding a page
1. Drop the exported HTML in `pages/` (e.g. `pages/08-despegue.html`).
2. Add an entry to the `PAGES` map in `index.html`.

## Run locally
```bash
python3 -m http.server 8000
```
Then open http://localhost:8000.

Fonts: Baloo 2 (SIL Open Font License 1.1), bundled inside the page files.
