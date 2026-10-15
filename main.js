// English by default, Spanish on request or for Spanish browsers. The choice is remembered.
const ES = {
  "skip": "Ir a los juegos",
  "nav.games": "Juegos",
  "nav.studio": "Estudio",
  "nav.contact": "Contacto",
  "hero.eyebrow": "Hecho en Argentina",
  "hero.title1": "Juegos chicos",
  "hero.title2": "que abren",
  "hero.title3": "algo.",
  "hero.lead": "Hechos para los momentos grandes: el clic cuando un puzzle por fin cede, el gusto de romperlo todo, las ganas de jugar una partida más. Inserta el disquete. Gira la llave.",
  "hero.cta": "Jugar STRIKE!",
  "hero.cta2": "Ver todos los disquetes",
  "hero.loading": "CARGANDO STRIKE!",
  "games.title": "La caja de disquetes",
  "games.sub": "Cada juego tiene su disquete. Algunos todavía están en blanco.",
  "tag.live": "Jugable",
  "tag.soon": "En el cajón",
  "tag.locked": "Bajo llave",
  "games.strike.genre": "Incremental · 20–30 min",
  "games.puzzle.title": "Un juego de puzzles sin nombre",
  "games.puzzle.genre": "Puzzle · en bocetos",
  "games.escape.title": "Un escape room",
  "games.escape.genre": "Escape room · primero encuentra la llave",
  "strike.eyebrow": "Disquete 01 · Ya se juega en el navegador",
  "strike.p1": "Ocho años. Cinco vacaciones rechazadas. Cinco copias del formulario 27-B. Le respondes a Recursos Humanos con una palabra, atas tu bola de bolos a un cable de red y desarmas la oficina, piso por piso.",
  "strike.f1": "pisos, de la Recepción al despacho del jefe",
  "strike.f2": "nodos en el organigrama de la empresa",
  "strike.f3": "cosas que opinan tus compañeros",
  "strike.cta": "Jugar gratis en itch.io",
  "strike.langs": "Español · English · Solo mouse",
  "studio.title": "Por qué un disquete y una llave",
  "studio.p1": "Un disquete guardaba una cosa chica y completa. Lo metías, cargaba y jugabas. Una llave abre algo que todavía no tenías que ver. Así son nuestros juegos: chicos, terminados y con algo escondido adentro.",
  "spec.capacity": "Capacidad",
  "spec.capacity.v": "1,44 MB de ideas",
  "spec.team": "Equipo",
  "spec.team.v": "Una persona, mucho café",
  "spec.formats": "Formatos",
  "spec.formats.v": "Incrementales, puzzles, escape rooms",
  "spec.write": "Protección",
  "spec.write.v": "Desactivada. Escuchamos a los jugadores.",
  "contact.title": "Escribe en la etiqueta",
  "contact.p": "¿Jugaste algo? ¿Encontraste un error? ¿Quieres saber cuándo sale el próximo disquete? Sigue al estudio en itch.io o manda un mensaje.",
  "contact.copy": "Copiar el correo",
  "contact.copied": "Copiado",
  "foot": "Inserta el disquete. Gira la llave."
};

const nodes = document.querySelectorAll("[data-i18n]");
const english = new Map([...nodes].map(n => [n.dataset.i18n, n.textContent]));
english.set("contact.copied", "Copied");
const langButton = document.getElementById("lang");
let current = "en";

function apply(lang) {
  current = lang;
  for (const node of nodes) {
    const key = node.dataset.i18n;
    node.textContent = (lang === "es" ? ES[key] : english.get(key)) ?? english.get(key);
  }
  document.documentElement.lang = lang;
  langButton.textContent = lang === "es" ? "EN" : "ES";
  langButton.setAttribute("aria-label", lang === "es" ? "Switch to English" : "Cambiar a español");
  labelTheme();
  try { localStorage.setItem("lang", lang); } catch (e) { /* private mode: not remembered */ }
}

// Night by default. The button names the mode it switches to.
const themeButton = document.getElementById("theme");
const isLight = () => document.documentElement.dataset.theme === "light";

function labelTheme() {
  const es = current === "es";
  themeButton.textContent = isLight() ? (es ? "NOCHE" : "NIGHT") : (es ? "DÍA" : "DAY");
  themeButton.setAttribute("aria-label", isLight()
    ? (es ? "Cambiar a modo noche" : "Switch to night mode")
    : (es ? "Cambiar a modo día" : "Switch to day mode"));
}

themeButton.addEventListener("click", () => {
  if (isLight()) delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = "light";
  try { localStorage.setItem("theme", isLight() ? "light" : "dark"); } catch (e) { /* not remembered */ }
  labelTheme();
});

let saved = null;
try { saved = localStorage.getItem("lang"); } catch (e) { saved = null; }
const initial = saved || ((navigator.language || "").toLowerCase().startsWith("es") ? "es" : "en");
if (initial === "es") apply("es");
else labelTheme();
langButton.addEventListener("click", () => apply(current === "es" ? "en" : "es"));

// Copy the email, falling back to selecting it.
const copyButton = document.getElementById("copy");
const mail = document.querySelector(".mail");
copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(mail.textContent.trim());
    const key = "contact.copied";
    copyButton.textContent = current === "es" ? ES[key] : english.get(key);
    setTimeout(() => apply(current), 1600);
  } catch (e) {
    const range = document.createRange();
    range.selectNodeContents(mail);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
  }
});
