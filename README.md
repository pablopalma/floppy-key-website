# Floppy Key — sitio web

Web del estudio. HTML, CSS y JS sin dependencias ni compilación.

- `index.html`: la página. Los textos en inglés están en el HTML.
- `main.js`: los textos en español y el cambio de idioma (usa el idioma del navegador la primera vez y recuerda la elección).
- `styles.css`: colores y tipografías en las variables de `:root`.
- `assets/`: el ícono y las capturas de los juegos.

## Antes de publicar

- Cambiar `hola@floppykey.com` por el correo real (está en `index.html`).
- Revisar los enlaces a itch.io cuando la página de STRIKE! esté publicada.
- Reemplazar la captura de `assets/strike-orgchart.png` por una mejor o por un GIF.

## Publicar gratis

Cualquiera de estas sirve: GitHub Pages (subir la carpeta a un repositorio y activar Pages), Netlify o Cloudflare Pages (arrastrar la carpeta). Después se conecta el dominio `floppykey.com`.

## Probar en la computadora

```bash
python -m http.server 8765
```

Y abrir `http://localhost:8765`.
