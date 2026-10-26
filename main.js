// English by default, Spanish on request or for Spanish browsers. The choice is remembered.
const ES = {
  "skip": "Ir a los juegos",
  "nav.games": "Juegos",
  "nav.studio": "Estudio",
  "nav.contact": "Contacto",
  "nav.devblog": "Devblog",
  "skip.posts": "Ir a las entradas",
  "skip.post": "Ir a la entrada",
  "devblog.eyebrow": "Notas desde el taller",
  "devblog.sub": "Qué cambió en cada actualización, por qué cambió y qué viene. Lo más nuevo primero.",
  "devblog.all": "Todos los juegos",
  "devblog.read": "Leer la entrada",
  "devblog.empty": "Todavía no hay entradas de este juego.",
  "devblog.back": "← Todas las entradas",
  "devblog.inEnglish": "Esta entrada está escrita en inglés.",
  "devblog.inSpanish": "Esta entrada está escrita en español.",
  "devblog.play": "Jugar gratis en itch.io",
  "devblog.see": "Ver el juego",
  "devblog.more": "Más entradas de este juego",
  "devblog.newer": "Más reciente",
  "devblog.older": "Anterior",
  "hero.eyebrow": "Hecho en Argentina",
  "hero.title1": "Juegos chicos",
  "hero.title2": "que abren",
  "hero.title3": "algo.",
  "hero.lead": "Hechos para los momentos grandes: el clic cuando un puzzle por fin cede, el gusto de romperlo todo, las ganas de jugar una partida más. Inserta el disquete. Gira la llave.",
  "hero.cta": "Conocer The Seal Quest",
  "hero.cta2": "Ver todos los disquetes",
  "hero.loading": "CARGANDO THE SEAL QUEST",
  "games.title": "La caja de disquetes",
  "games.sub": "Cada juego tiene su disquete.",
  "tag.live": "Jugable",
  "tag.dev": "En desarrollo",
  "games.strike.genre": "Incremental · 20–30 min",
  "games.sealquest.genre": "RPG incremental · caza a los épicos",
  "strike.eyebrow": "Disquete 01 · Ya se juega en el navegador",
  "strike.p1": "Ocho años. Cinco vacaciones rechazadas. Cinco copias del formulario 27-B. Le respondes a Recursos Humanos con una palabra, atas tu bola de bolos a un cable de red y desarmas la oficina, piso por piso.",
  "strike.f1": "pisos, de la Recepción al despacho del jefe",
  "strike.f2": "nodos en el organigrama de la empresa",
  "strike.f3": "cosas que opinan tus compañeros",
  "strike.cta": "Jugar gratis en itch.io",
  "strike.langs": "Español · English · Solo mouse",
  "seal.eyebrow": "Disquete 02 · Demo gratis ya disponible",
  "seal.tagline": "Cada épico que cazas despierta algo más grande.",
  "seal.p1": "Un RPG incremental de defensa. Aguanta el claro con tu compañía, apunta a lo que se acerque, gasta lo que ganas y vuelve por más. Caza a los épicos y viste lo que dejan.",
  "seal.f1": "épicos para cazar en la demo gratis",
  "seal.f2": "héroes peleando a tu lado",
  "seal.f3": "encantamientos en la forja de Brunna, y nunca fallan",
  "seal.cta": "Jugar gratis en itch.io",
  "seal.more": "Ver el juego",
  "seal.alt": "The Seal Quest: cayó el Rey Zarza, y su cofre de oro y su arco esperan en el claro.",
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
  for (const img of document.querySelectorAll("[data-i18n-alt]")) {
    if (!img.dataset.alt) img.dataset.alt = img.alt;
    img.alt = lang === "es" ? (ES[img.dataset.i18nAlt] ?? img.dataset.alt) : img.dataset.alt;
  }
  document.documentElement.lang = lang;
  langButton.textContent = lang === "es" ? "EN" : "ES";
  langButton.setAttribute("aria-label", lang === "es" ? "Switch to English" : "Cambiar a español");
  formatDates();
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
// English by default; Spanish only when the visitor chose it.
const initial = saved === "es" ? "es" : "en";
if (initial === "es") apply("es");
else { formatDates(); labelTheme(); }
langButton.addEventListener("click", () => apply(current === "es" ? "en" : "es"));

// Devblog dates are written in English; show them in the visitor's language.
function formatDates() {
  for (const time of document.querySelectorAll("time[data-date]")) {
    const [y, m, d] = time.dateTime.split("-").map(Number);
    time.textContent = new Date(y, m - 1, d).toLocaleDateString(current === "es" ? "es-AR" : "en-US",
      { year: "numeric", month: "long", day: "numeric" });
  }
}

// Devblog index: filter by game with ?game=<id>, so a filtered list can be shared.
const filters = document.querySelectorAll(".filter[data-filter]");
if (filters.length) {
  const posts = document.querySelectorAll(".posts > li[data-game]");
  const empty = document.querySelector(".posts-empty");
  const show = game => {
    let visible = 0;
    for (const post of posts) {
      post.hidden = game !== "" && post.dataset.game !== game;
      if (!post.hidden) visible++;
    }
    for (const filter of filters) {
      if (filter.dataset.filter === game) filter.setAttribute("aria-current", "true");
      else filter.removeAttribute("aria-current");
    }
    if (empty) empty.hidden = visible > 0;
  };
  for (const filter of filters) {
    filter.addEventListener("click", event => {
      event.preventDefault();
      show(filter.dataset.filter);
      const url = new URL(location.href);
      if (filter.dataset.filter) url.searchParams.set("game", filter.dataset.filter);
      else url.searchParams.delete("game");
      history.replaceState(null, "", url);
    });
  }
  show(new URLSearchParams(location.search).get("game") || "");
}

// Copy the email, falling back to selecting it. Only the home page has it.
const copyButton = document.getElementById("copy");
const mail = document.querySelector(".mail");
copyButton?.addEventListener("click", async () => {
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
