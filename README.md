# Floppy Key — sitio web

Web del estudio. HTML, CSS y JS sin dependencias ni compilación.

- `index.html`: la página. Los textos en inglés están en el HTML.
- `main.js`: los textos en español y el cambio de idioma (usa el idioma del navegador la primera vez y recuerda la elección).
- `styles.css`: colores y tipografías en las variables de `:root`.
- `assets/`: el ícono y las capturas de los juegos.
- `devblog/`: las entradas del devblog. Cada carpeta es una entrada (`post.md` con sus imágenes) y las páginas HTML se generan con `tools/build_devblog.py`.

## Agregar una entrada al devblog

1. Copiar `devblog/_plantilla/` a una carpeta nueva dentro de `devblog/`. El nombre de la carpeta es la dirección de la entrada: por ejemplo `strike-1-3-0`, sin espacios ni puntos.
2. Poner en esa carpeta las imágenes, los GIF y la portada de 630×500.
3. Completar `post.md`. Arriba, entre las líneas `---`, van los datos: `title`, `date` (AAAA-MM-DD), `game`, `cover` (el nombre del archivo de la portada) y `summary` (el resumen de la lista). `version` es opcional, y `lang: es` marca una entrada escrita en español (por defecto se asume inglés). Debajo va el texto en Markdown, el mismo del devlog de itch.io; las imágenes se nombran sin carpeta: `![Pie de foto](mi-gif.gif)`.
   - **Traducción (opcional):** un `post.es.md` en la misma carpeta (o `post.en.md` si la entrada está escrita en español), con `title` y `summary` arriba y el texto traducido debajo. Usa las mismas imágenes. Con traducción, el botón de idioma cambia el título, el resumen y el texto, y desaparece el aviso "Esta entrada está escrita en inglés".
4. Correr `python tools/build_devblog.py`. Genera la página de cada entrada, el índice `devblog/index.html` y el feed `devblog/feed.xml`. Si falta un dato o una imagen, avisa qué y no escribe nada.
5. Revisarlo en local (abajo) y subir todo, incluidos los HTML generados: el sitio no se compila al publicar.

Los HTML del devblog se generan: los cambios se hacen en `post.md`, en `styles.css` o en el script, nunca a mano en esas páginas. Las carpetas que empiezan con `_` no se publican como entradas.

Para un juego nuevo, agregarlo en `devblog/games.json` con su nombre, su nombre corto (el de la etiqueta y el filtro), su color y el enlace para jugarlo (`url`). Si todavía no se puede jugar, en lugar de `url` va `page`, la página del juego dentro del sitio (por ejemplo `seal-quest/index.html`), y el botón de las entradas dice "Ver el juego". `game` en `post.md` usa la clave de ese archivo. El filtro por juego aparece solo con los juegos que tienen entradas, y se puede compartir: `devblog/index.html?game=strike`.

`site` en `games.json` es la dirección pública del sitio. Se usa para las vistas previas al compartir un enlace y para el feed; hay que cambiarla si el dominio no termina siendo `floppykey.com`.

## Ranking (The Seal Quest)

`seal-quest/index.html` muestra en **Top heroes** los 20 primeros del ranking del juego (`?action=top`), leídos de su planilla (`tools/ranking-sheet/Ranking.gs` en el repositorio del juego). Los raids elementales, dentro de "Coming in the full game", son texto fijo.

La dirección está en `data-endpoint`, en la etiqueta `<body>` de `seal-quest/index.html`: la URL de la aplicación web de la planilla, la misma que `rankingEndpoint` en el `GameConfig` del juego. Si está vacía, el ranking dice que abre pronto; si la planilla no responde, lo dice.

El apoyo hacia Steam (meta, Ko-fi y Wall of Noble Heroes) se quitó el 26 de octubre de 2026: no se piden donaciones.

## Libro de la mitología (The Seal Quest)

`seal-quest/mitologia/index.html` es el libro *Los sueños de Ormaz* / *The Dreams of Ormaz*, en inglés y en español, con las láminas adentro del archivo. Usa el mismo idioma que el resto del sitio (`lang` en `localStorage`, inglés por defecto) y tiene su propio botón ES/EN. Se enlaza desde el menú de `seal-quest/index.html` ("Lore" / "Mitología") y desde un botón al final de la sección World. Sale de `docs/web/los-suenos-de-ormaz.html` del repositorio del juego, que se arma desde `docs/mitologia.md`; esta copia suma el enlace de vuelta "← The Seal Quest" y el ícono. Si cambia la mitología, se rehace allá y se vuelve a copiar.

## Just Tap

`just-tap/index.html` es la página del juego, con su propia estética (papel, tinta y Cormorant Garamond). Los medios de `just-tap/media/` salen del repositorio del juego (`D:\Proyectos Pablo\just-tap-godot`): las capturas y los loops, del tráiler (`tools/make_trailer.ps1`), y el loop de la portada (`loop-colour.mp4`), de `tools/hero_clip.tscn`, que graba el color volviendo sin subtítulos ni títulos. El enlace a itch.io (`https://floppykey.itch.io/just-tap`) funciona cuando la página de itch deja de ser borrador.
## Antes de publicar

- Cambiar `hola@floppykey.com` por el correo real (está en `index.html`).
- Revisar los enlaces a itch.io cuando la página de STRIKE! esté publicada.
- Reemplazar la captura de `assets/strike-orgchart.png` por una mejor o por un GIF.
- Confirmar la dirección de `site` en `devblog/games.json`.
- Completar `data-endpoint` en `seal-quest/index.html` cuando la planilla del ranking esté publicada.

## Publicar gratis

Cualquiera de estas sirve: GitHub Pages (subir la carpeta a un repositorio y activar Pages), Netlify o Cloudflare Pages (arrastrar la carpeta). Después se conecta el dominio `floppykey.com`. El archivo vacío `.nojekyll` evita que GitHub Pages procese los `post.md` con Jekyll.

## Probar en la computadora

```bash
python -m http.server 8765
```

Y abrir `http://localhost:8765`.
