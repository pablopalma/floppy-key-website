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
