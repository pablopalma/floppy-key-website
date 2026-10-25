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
4. Correr `python tools/build_devblog.py`. Genera la página de cada entrada, el índice `devblog/index.html` y el feed `devblog/feed.xml`. Si falta un dato o una imagen, avisa qué y no escribe nada.
5. Revisarlo en local (abajo) y subir todo, incluidos los HTML generados: el sitio no se compila al publicar.

Los HTML del devblog se generan: los cambios se hacen en `post.md`, en `styles.css` o en el script, nunca a mano en esas páginas. Las carpetas que empiezan con `_` no se publican como entradas.

Para un juego nuevo, agregarlo en `devblog/games.json` con su nombre, su nombre corto (el de la etiqueta y el filtro), su color y el enlace para jugarlo (`url`). Si todavía no se puede jugar, en lugar de `url` va `page`, la página del juego dentro del sitio (por ejemplo `seal-quest/index.html`), y el botón de las entradas dice "Ver el juego". `game` en `post.md` usa la clave de ese archivo. El filtro por juego aparece solo con los juegos que tienen entradas, y se puede compartir: `devblog/index.html?game=strike`.

`site` en `games.json` es la dirección pública del sitio. Se usa para las vistas previas al compartir un enlace y para el feed; hay que cambiarla si el dominio no termina siendo `floppykey.com`.

## Ranking y apoyo hacia Steam (The Seal Quest)

`seal-quest/index.html` tiene tres secciones que leen la planilla del ranking del juego (`tools/ranking-sheet/Ranking.gs` en el repositorio del juego):

- **Los raids elementales**, dentro de "Coming in the full game". Es texto fijo.
- **Top heroes**: los 20 primeros del ranking (`?action=top`).
- **Let's take the game to Steam**: la barra hacia la meta, el botón de Ko-fi y el Wall of Noble Heroes (`?action=support`). Los tres primeros van en naranja, amarillo y gris con aura, y el resto en blanco.

La configuración está en la etiqueta `<body>` de `seal-quest/index.html`:

- `data-endpoint`: la URL de la aplicación web de la planilla, la misma que `rankingEndpoint` en el `GameConfig` del juego.
- `data-kofi`: la página de Ko-fi del proyecto, por ejemplo `https://ko-fi.com/floppykey`.

Si están vacíos, las secciones dicen que abren pronto y el botón de Ko-fi aparece desactivado. Si la planilla no responde, lo dicen y el botón sigue funcionando.

## Antes de publicar

- Cambiar `hola@floppykey.com` por el correo real (está en `index.html`).
- Revisar los enlaces a itch.io cuando la página de STRIKE! esté publicada.
- Reemplazar la captura de `assets/strike-orgchart.png` por una mejor o por un GIF.
- Confirmar la dirección de `site` en `devblog/games.json`.
- Completar `data-endpoint` y `data-kofi` en `seal-quest/index.html` cuando la planilla del ranking y la página de Ko-fi estén publicadas.

## Publicar gratis

Cualquiera de estas sirve: GitHub Pages (subir la carpeta a un repositorio y activar Pages), Netlify o Cloudflare Pages (arrastrar la carpeta). Después se conecta el dominio `floppykey.com`. El archivo vacío `.nojekyll` evita que GitHub Pages procese los `post.md` con Jekyll.

## Probar en la computadora

```bash
python -m http.server 8765
```

Y abrir `http://localhost:8765`.
