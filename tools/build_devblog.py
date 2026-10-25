"""Builds the devblog: one static page per entry, the index and the RSS feed.

Each entry is a folder in devblog/ with a post.md (front matter + Markdown) and its images.
A translation may sit beside it as post.es.md (or post.en.md for an entry written in Spanish):
its own title, summary and text, shown when the visitor picks that language.
Folders starting with "_" are skipped (the template lives there). Python standard library only.

    python tools/build_devblog.py
"""
import datetime
import html
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "devblog"
REQUIRED = ("title", "date", "game", "cover", "summary")
FONTS = "https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Figtree:wght@400;500;700;800&family=Gochi+Hand&family=VT323&display=swap"

errors = []


def esc(text):
    return html.escape(str(text), quote=True)


def english_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d:%B} {d.day}, {d.year}"


# ---------- Images ----------

def image_size(path):
    """Width and height of a PNG, GIF or JPEG, or None."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:3] == b"GIF":
        return struct.unpack("<HH", data[6:10])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + length
    return None


def img_tag(folder, src, alt, eager=False, where=""):
    attrs = f'src="{esc(src)}" alt="{esc(alt)}"'
    if not re.match(r"^[a-z]+://", src):
        path = folder / src
        if not path.exists():
            errors.append(f"{where}: no existe la imagen {src}")
        size = image_size(path)
        if size:
            attrs += f' width="{size[0]}" height="{size[1]}"'
    attrs += ' decoding="async"' if eager else ' loading="lazy" decoding="async"'
    return f"<img {attrs}>"


# ---------- Markdown (the subset the devlogs use) ----------

def inline(text, folder, where):
    codes = []

    def keep_code(m):
        codes.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: img_tag(folder, html.unescape(m.group(2)), html.unescape(m.group(1)), where=where), text)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        external = ' target="_blank" rel="noopener"' if re.match(r"^https?://", url) else ""
        return f'<a href="{esc(url)}"{external}>{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_(?![\s_])(.+?)(?<![\s_])_(?![_\w])", r"<em>\1</em>", text)
    text = re.sub(r" *\n", "<br>\n", text)  # a line break in the Markdown is a line break on the page, as on itch.io
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
FIGURE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$')
ITEM = re.compile(r"^\s{0,3}([-*+]|\d+[.)])\s+(.*)$")
RULE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")


def starts_block(s):
    return bool(HEADING.match(s) or ITEM.match(s) or s.startswith((">", "```")) or RULE.match(s) or FIGURE.match(s))


def slugify(text):
    text = re.sub(r"<[^>]+>|[*_`]", "", text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


class Renderer:
    def __init__(self, folder, where):
        self.folder, self.where = folder, where
        self.figures = 0

    def inline(self, text):
        return inline(text, self.folder, self.where)

    def render(self, lines):
        out, i = [], 0
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                i += 1
            elif s.startswith("```"):
                body, i = [], i + 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    body.append(lines[i])
                    i += 1
                out.append(f"<pre><code>{html.escape(chr(10).join(body), quote=False)}</code></pre>")
                i += 1
            elif m := HEADING.match(s):
                level = max(2, len(m.group(1)))  # the entry's title is the only h1
                out.append(f'<h{level} id="{slugify(m.group(2))}">{self.inline(m.group(2))}</h{level}>')
                i += 1
            elif RULE.match(s):
                out.append("<hr>")
                i += 1
            elif m := FIGURE.match(s):
                alt, src, caption = m.group(1), m.group(2), m.group(3) or m.group(1)
                tag = img_tag(self.folder, src, alt, eager=self.figures == 0, where=self.where)
                self.figures += 1
                cap = f"<figcaption>{self.inline(caption)}</figcaption>" if caption else ""
                out.append(f"<figure>{tag}{cap}</figure>")
                i += 1
            elif s.startswith(">"):
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(re.sub(r"^\s*> ?", "", lines[i]))
                    i += 1
                out.append(f"<blockquote>{self.render(quote)}</blockquote>")
            elif ITEM.match(lines[i]):
                i = self.list(lines, i, out)
            elif s.startswith("<"):
                block = []
                while i < len(lines) and lines[i].strip():
                    block.append(lines[i])
                    i += 1
                out.append("\n".join(block))
            else:
                para = []
                while i < len(lines) and lines[i].strip() and not (para and starts_block(lines[i].strip())):
                    para.append(lines[i].lstrip())
                    i += 1
                out.append(f"<p>{self.inline(chr(10).join(para))}</p>")
        return "\n".join(out)

    def list(self, lines, i, out):
        ordered = ITEM.match(lines[i]).group(1)[0].isdigit()
        items = []
        while i < len(lines):
            m = ITEM.match(lines[i])
            s = lines[i].strip()
            if m and m.group(1)[0].isdigit() == ordered:
                items.append([m.group(2)])
            elif s and items and not starts_block(s):
                items[-1].append(s)  # continuation of the previous item
            elif not s and i + 1 < len(lines) and ITEM.match(lines[i + 1]):
                pass  # loose list: keep going
            else:
                break
            i += 1
        tag = "ol" if ordered else "ul"
        body = "".join(f"<li>{self.inline(chr(10).join(item))}</li>" for item in items)
        out.append(f"<{tag}>{body}</{tag}>")
        return i


# ---------- Entries ----------

def read_entry(folder, games):
    where = f"devblog/{folder.name}/post.md"
    text = (folder / "post.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        errors.append(f"{where}: falta el bloque de datos entre --- al principio")
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[key.strip().lower()] = value
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        errors.append(f"{where}: faltan datos: {', '.join(missing)}")
        return None
    try:
        datetime.date.fromisoformat(meta["date"])
    except ValueError:
        errors.append(f"{where}: la fecha tiene que ser AAAA-MM-DD (dice {meta['date']})")
        return None
    if meta["game"] not in games:
        errors.append(f"{where}: el juego '{meta['game']}' no está en devblog/games.json")
        return None
    if not (folder / meta["cover"]).exists():
        errors.append(f"{where}: no existe la portada {meta['cover']}")
    body = m.group(2).strip().splitlines()
    # The front matter title wins; drop a leading "# Title" pasted from itch.io.
    if body and body[0].startswith("# "):
        body = body[1:]
    meta["slug"] = folder.name
    meta["lang"] = meta.get("lang", "en")
    meta["html"] = Renderer(folder, where).render(body)
    meta["alt"] = read_translation(folder, "es" if meta["lang"] == "en" else "en")
    return meta


def read_translation(folder, lang):
    """The entry in its other language (post.es.md or post.en.md): title, summary and text, or None."""
    path = folder / f"post.{lang}.md"
    if not path.exists():
        return None
    where = f"devblog/{folder.name}/{path.name}"
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        errors.append(f"{where}: falta el bloque de datos entre --- al principio")
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[key.strip().lower()] = value
    missing = [k for k in ("title", "summary") if not meta.get(k)]
    if missing:
        errors.append(f"{where}: faltan datos: {', '.join(missing)}")
        return None
    body = m.group(2).strip().splitlines()
    if body and body[0].startswith("# "):
        body = body[1:]
    return {"lang": lang, "title": meta["title"], "summary": meta["summary"], "html": Renderer(folder, where).render(body)}


def both(entry, key, tag, cls):
    """The entry's title or summary, plus its translation when there is one: each shows in its language."""
    first = f'<{tag} class="{cls}" lang="{entry["lang"]}"'
    alt = entry.get("alt")
    if not alt:
        return f'{first}>{esc(entry[key])}</{tag}>'
    return (f'{first} data-only="{entry["lang"]}">{esc(entry[key])}</{tag}>'
            f'<{tag} class="{cls}" lang="{alt["lang"]}" data-only="{alt["lang"]}">{esc(alt[key])}</{tag}>')


# ---------- Pages ----------

def page(root, title, description, main, skip, og="", feed=""):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
{og}  <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
  <link rel="alternate" type="application/rss+xml" title="Floppy Key devblog" href="{root}devblog/feed.xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="{root}styles.css">
  <script>
    try {{ if (localStorage.getItem("theme") === "light") document.documentElement.dataset.theme = "light"; }} catch (e) {{}}
  </script>
</head>
<body>
  <!-- Generated by tools/build_devblog.py from post.md. Edit the Markdown, not this file. -->
  {skip}

  <header class="top">
    <a class="brand" href="{root}index.html" aria-label="Floppy Key, indie game studio, home">
      <svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true"><use href="#floppy"/></svg>
      <span class="brand-text">
        <span class="brand-name">Floppy&nbsp;Key</span>
        <span class="brand-sub">Indie game studio</span>
      </span>
    </a>
    <nav class="nav" aria-label="Main">
      <a href="{root}index.html#games" data-i18n="nav.games">Games</a>
      <a href="{root}devblog/index.html" data-i18n="nav.devblog" aria-current="page">Devblog</a>
      <a href="{root}index.html#studio" data-i18n="nav.studio">Studio</a>
      <a href="{root}index.html#contact" data-i18n="nav.contact">Contact</a>
      <span class="toggles">
        <button class="chip" id="theme" type="button">DAY</button>
        <button class="chip" id="lang" type="button" aria-label="Cambiar a español">ES</button>
      </span>
    </nav>
  </header>

{main}

  <footer class="foot">
    <span>© 2026 Floppy Key</span>
    <span data-i18n="foot">Insert disk. Turn key.</span>
  </footer>

  <svg width="0" height="0" style="position:absolute" aria-hidden="true">
    <symbol id="floppy" viewBox="0 0 64 64">
      <path d="M6 4h46l8 8v44a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8a4 4 0 0 1 4-4z" style="fill: var(--body, var(--disk-ink))"/>
      <rect x="16" y="4" width="30" height="20" rx="1.5" style="fill: var(--metal)"/>
      <circle cx="25" cy="14" r="5" style="fill: var(--disk-ink)"/>
      <path d="M29 12.5h12v3h-2v3h-3v-3h-2v2h-3v-2h-2z" style="fill: var(--disk-ink)"/>
      <rect x="11" y="32" width="42" height="24" rx="2" style="fill: var(--label)"/>
      <rect x="15" y="38" width="34" height="2" rx="1" style="fill: var(--disk-rule)"/>
      <rect x="15" y="44" width="34" height="2" rx="1" style="fill: var(--disk-rule)"/>
      <rect x="15" y="50" width="22" height="2" rx="1" style="fill: var(--disk-rule)"/>
    </symbol>
  </svg>

  <script src="{root}main.js"></script>
</body>
</html>
"""


def meta_line(entry, game, href_game):
    version = f'<span class="post-version">{esc(entry["version"])}</span>' if entry.get("version") else ""
    tag = f'<span class="tag tag-game">{esc(game["short"])}</span>'
    if href_game:
        tag = f'<a class="tag tag-game" href="{href_game}">{esc(game["short"])}</a>'
    return (f'<p class="post-meta">{tag}{version}'
            f'<time datetime="{entry["date"]}" data-date>{english_date(entry["date"])}</time></p>')


def og_tags(site, title, description, url, image, kind):
    if not site:
        return ""
    site = site.rstrip("/")
    return (f'  <meta property="og:type" content="{kind}">\n'
            f'  <meta property="og:site_name" content="Floppy Key">\n'
            f'  <meta property="og:title" content="{esc(title)}">\n'
            f'  <meta property="og:description" content="{esc(description)}">\n'
            f'  <meta property="og:url" content="{site}/{url}">\n'
            f'  <meta property="og:image" content="{site}/{image}">\n'
            f'  <meta name="twitter:card" content="summary_large_image">\n')


def lang_note(entry):
    if entry.get("alt"):
        return ""
    if entry["lang"] == "es":
        return '<p class="lang-note" data-for="en" data-i18n="devblog.inSpanish">This entry is written in Spanish.</p>'
    return '<p class="lang-note" data-for="es" data-i18n="devblog.inEnglish">Esta entrada está escrita en inglés.</p>'


def build_index(entries, games, site):
    counts = {}
    for e in entries:
        counts[e["game"]] = counts.get(e["game"], 0) + 1
    filters = ['<a class="filter" href="index.html" data-filter="" aria-current="true">'
               f'<span data-i18n="devblog.all">All games</span> <span class="filter-count">{len(entries)}</span></a>']
    for gid, game in games.items():
        if gid in counts:
            filters.append(f'<a class="filter" href="index.html?game={gid}" data-filter="{gid}" style="--body: {game["color"]}">'
                           f'<span class="filter-dot" aria-hidden="true"></span>{esc(game["short"])} '
                           f'<span class="filter-count">{counts[gid]}</span></a>')
    cards = []
    for e in entries:
        game = games[e["game"]]
        size = image_size(BLOG / e["slug"] / e["cover"]) or (630, 500)
        lazy = "" if not cards else ' loading="lazy"'
        cover = (f'<img class="post-card-cover" src="{e["slug"]}/{esc(e["cover"])}" alt="" '
                 f'width="{size[0]}" height="{size[1]}"{lazy} decoding="async">')
        cards.append(f"""      <li data-game="{e['game']}">
        <a class="post-card" href="{e['slug']}/index.html" style="--body: {game['color']}">
          {cover}
          <span class="post-card-body">
            {meta_line(e, game, None).replace('<p ', '<span ', 1).replace('</p>', '</span>')}
            {both(e, 'title', 'span', 'post-card-title')}
            {both(e, 'summary', 'span', 'post-card-summary')}
            <span class="post-card-read" data-i18n="devblog.read">Read entry</span>
          </span>
        </a>
      </li>""")
    main = f"""  <main id="posts" class="blog">
    <section class="blog-head">
      <p class="eyebrow" data-i18n="devblog.eyebrow">Notes from the workbench</p>
      <h1 class="blog-title">Devblog</h1>
      <p class="blog-sub" data-i18n="devblog.sub">What changed in every update, why it changed, and what's coming next. Newest first.</p>
    </section>

    <nav class="filters" aria-label="Filter by game">
      {chr(10).join('      ' + f for f in filters).strip()}
    </nav>

    <ul class="posts">
{chr(10).join(cards)}
    </ul>
    <p class="posts-empty" hidden data-i18n="devblog.empty">No entries for this game yet.</p>
  </main>"""
    description = "Devlogs from Floppy Key: what changed in every update of our games, and why."
    og = og_tags(site, "Floppy Key devblog", description, "devblog/index.html",
                 f"devblog/{entries[0]['slug']}/{entries[0]['cover']}" if entries else "assets/itch-banner.png", "website")
    skip = '<a class="skip" href="#posts" data-i18n="skip.posts">Skip to the entries</a>'
    return page("../", "Devblog · Floppy Key", description, main, skip, og)


def prose(entry):
    alt = entry.get("alt")
    if not alt:
        return f'<div class="prose" lang="{entry["lang"]}">\n{entry["html"]}\n      </div>'
    return (f'<div class="prose" lang="{entry["lang"]}" data-only="{entry["lang"]}">\n{entry["html"]}\n      </div>\n'
            f'      <div class="prose" lang="{alt["lang"]}" data-only="{alt["lang"]}">\n{alt["html"]}\n      </div>')


def build_entry(entry, newer, older, games, site):
    game = games[entry["game"]]
    nav = []
    if newer:
        nav.append(f'<a class="post-nav-link newer" href="../{newer["slug"]}/index.html">'
                   f'<span class="post-nav-dir" data-i18n="devblog.newer">Newer</span>'
                   f'{both(newer, "title", "span", "post-nav-title")}</a>')
    if older:
        nav.append(f'<a class="post-nav-link older" href="../{older["slug"]}/index.html">'
                   f'<span class="post-nav-dir" data-i18n="devblog.older">Older</span>'
                   f'{both(older, "title", "span", "post-nav-title")}</a>')
    nav_html = f'\n      <nav class="post-nav" aria-label="More entries">{"".join(nav)}</nav>' if nav else ""
    # A game that isn't out yet links to its own page on the site instead of to itch.io.
    if game.get("page"):
        play = f'<a class="btn btn-primary" href="../../{esc(game["page"])}" data-i18n="devblog.see">See the game</a>'
    elif game.get("url"):
        play = f'<a class="btn btn-primary" href="{esc(game["url"])}" target="_blank" rel="noopener" data-i18n="devblog.play">Play free on itch.io</a>'
    else:
        play = ""
    main = f"""  <main id="post" class="blog">
    <article class="post" style="--body: {game['color']}">
      <a class="back" href="../index.html" data-i18n="devblog.back">← All entries</a>
      <header class="post-head">
        {meta_line(entry, game, f"../index.html?game={entry['game']}")}
        {both(entry, 'title', 'h1', 'post-title')}
        {lang_note(entry)}
      </header>
      {prose(entry)}
      <aside class="post-cta">
        <svg class="post-cta-disk" viewBox="0 0 64 64" aria-hidden="true"><use href="#floppy"/></svg>
        <div class="post-cta-copy">
          <p class="post-cta-game">{esc(game['name'])}</p>
          <div class="actions">
            {play}
            <a class="btn btn-ghost" href="../index.html?game={entry['game']}" data-i18n="devblog.more">More entries about this game</a>
          </div>
        </div>
      </aside>{nav_html}
    </article>
  </main>"""
    title = f"{entry['title']} · {game['short']} devblog · Floppy Key"
    og = og_tags(site, f"{game['short']} {entry.get('version', '')}: {entry['title']}".replace("  ", " "),
                 entry["summary"], f"devblog/{entry['slug']}/index.html", f"devblog/{entry['slug']}/{entry['cover']}", "article")
    skip = '<a class="skip" href="#post" data-i18n="skip.post">Skip to the entry</a>'
    return page("../../", title, entry["summary"], main, skip, og)


def build_feed(entries, games, site):
    site = (site or "").rstrip("/")
    items = []
    for e in entries[:30]:
        d = datetime.date.fromisoformat(e["date"])
        stamp = datetime.datetime(d.year, d.month, d.day, 12, tzinfo=datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        link = f"{site}/devblog/{e['slug']}/index.html"
        items.append(f"""  <item>
    <title>{esc(games[e['game']]['short'] + ' ' + e.get('version', '') + ': ' + e['title'])}</title>
    <link>{esc(link)}</link>
    <guid>{esc(link)}</guid>
    <pubDate>{stamp}</pubDate>
    <category>{esc(games[e['game']]['name'])}</category>
    <description>{esc(e['summary'])}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
  <title>Floppy Key devblog</title>
  <link>{esc(site)}/devblog/index.html</link>
  <description>What changed in every update of Floppy Key's games, and why.</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"  {path.relative_to(ROOT).as_posix()}")


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    config = json.loads((BLOG / "games.json").read_text(encoding="utf-8"))
    games, site = config["games"], config.get("site", "")
    entries = []
    for folder in sorted(BLOG.iterdir()):
        if folder.is_dir() and not folder.name.startswith(("_", ".")) and (folder / "post.md").exists():
            entry = read_entry(folder, games)
            if entry:
                entries.append(entry)
    if errors:
        print("No se generó nada. Hay que corregir:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    entries.sort(key=lambda e: (e["date"], e["slug"]), reverse=True)
    print(f"Devblog: {len(entries)} entradas")
    for i, entry in enumerate(entries):
        newer = entries[i - 1] if i > 0 else None
        older = entries[i + 1] if i + 1 < len(entries) else None
        write(BLOG / entry["slug"] / "index.html", build_entry(entry, newer, older, games, site))
    write(BLOG / "index.html", build_index(entries, games, site))
    write(BLOG / "feed.xml", build_feed(entries, games, site))


if __name__ == "__main__":
    main()
