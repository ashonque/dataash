"""Write the decision articles from one template.

    python build-articles.py

The methodology pages answer "what is X". These answer "which one", for the
searches that are really decisions: type 1 or type 2, do I need staging,
Kimball or Data Vault. A decision article has a different shape from a
methodology profile - the question first, the short answer second, then the
reasoning - so it has a template of its own rather than a stretched copy of
the other one.

The words live in `articles.py`; this is the shape. The styles, the escaping
and the schema helpers are borrowed from `build-methodology-pages.py`, so the
three families of page cannot drift apart in their head or their look. That
file's name has hyphens in it, hence the import by path.
"""
import importlib.util
import io
import json
import os

SITE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dataash.de/"
HUB = "data-warehouse-methodologies.html"

_spec = importlib.util.spec_from_file_location(
    "methodology_gen", os.path.join(SITE, "build-methodology-pages.py"))
_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gen)
STYLE, esc, plain, jsonstr = _gen.STYLE, _gen.esc, _gen.plain, _gen.jsonstr

# What the decision pages add to the shared styles: a boxed short answer at
# the top, and a two-column verdict table.
EXTRA_STYLE = """
    .answer {
      background: var(--navy-700); color: #fff; border-radius: var(--radius);
      padding: 22px 26px; margin: 0 0 34px; font-size: 18px; line-height: 1.6;
    }
    .answer strong { color: #fff; }
    .answer a { color: #fff; text-decoration: underline; text-underline-offset: 3px; }
    .answer p { margin: 0 0 10px; }
    .answer p:last-child { margin: 0; }
    .answer .lbl { font-size: 12.5px; text-transform: uppercase; letter-spacing: .1em;
                   color: var(--navy-100); font-weight: 700; margin-bottom: 8px; }
    table td:first-child { font-weight: 600; color: var(--navy-900); }
    .related { margin: 44px 0 0; }
    .related ul { list-style: none; padding: 0; margin: 0; }
    .related li { margin: 0 0 8px; }
    .related a { font-weight: 600; text-decoration: none; }
    .related a:hover { text-decoration: underline; }
    .related span { color: var(--ink-dim); font-weight: 400; }
"""


def block(item):
    """One content block, whichever kind it is."""
    kind, value = next(iter(item.items()))
    if kind == "p":
        return "  <p>%s</p>" % value
    if kind == "h3":
        return "  <h3>%s</h3>" % esc(value)
    if kind == "ul":
        return "  <ul>\n%s\n  </ul>" % "\n".join("    <li>%s</li>" % li for li in value)
    if kind == "ol":
        return "  <ol>\n%s\n  </ol>" % "\n".join("    <li>%s</li>" % li for li in value)
    if kind == "code":
        return "  <pre><code>%s</code></pre>" % esc(value)
    if kind == "note":
        return '  <div class="note">\n    <p>%s</p>\n  </div>' % value
    if kind == "table":
        head, rows = value["head"], value["rows"]
        out = ['  <div class="wide">', "    <table>",
               "      <thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % esc(h) for h in head),
               "      <tbody>"]
        for row in rows:
            out.append("        <tr>%s</tr>" % "".join("<td>%s</td>" % cell for cell in row))
        out += ["      </tbody>", "    </table>", "  </div>"]
        return "\n".join(out)
    raise ValueError("unknown block kind %r" % kind)


def body(art, all_articles):
    out = []
    add = out.append
    add('  <nav class="crumbs" aria-label="Breadcrumb">')
    add('    <a href="/">Netune</a> &rsaquo; '
        '<a href="/%s">Data warehouse methodologies</a> &rsaquo; %s' % (HUB, esc(art["crumb"])))
    add("  </nav>")
    add("  <h1>%s</h1>" % esc(art["h1"]))
    add('  <p class="standfirst">%s</p>' % art["standfirst"])

    add('  <div class="answer">')
    add('    <div class="lbl">The short answer</div>')
    for para in art["answer"]:
        add("    <p>%s</p>" % para)
    add("  </div>")

    for section in art["sections"]:
        add('  <h2 id="%s">%s</h2>' % (section["id"], esc(section["h2"])))
        for item in section["blocks"]:
            add(block(item))

    add('  <h2 id="faq">Questions people ask</h2>')
    add('  <section class="faq">')
    for item in art["faq"]:
        add('    <div class="faq-item">')
        add("      <h3>%s</h3>" % esc(item["q"]))
        add("      <p>%s</p>" % item["a"])
        add("    </div>")
    add("  </section>")

    add('  <section class="related">')
    add("    <h2>Read next</h2>")
    add("    <ul>")
    for slug, label, why in art["related"]:
        add('      <li><a href="/%s">%s</a> <span>&mdash; %s</span></li>' % (slug, esc(label), esc(why)))
    for other in all_articles:
        if other["slug"] != art["slug"]:
            add('      <li><a href="/%s">%s</a> <span>&mdash; %s</span></li>'
                % (other["slug"], esc(other["short"]), esc(other["oneline"])))
    add('      <li><a href="/%s">All eight methodologies compared</a> '
        '<span>&mdash; and how to choose between them</span></li>' % HUB)
    add("    </ul>")
    add("  </section>")

    add('  <div class="cta">')
    add("    <h2>%s</h2>" % esc(art["cta_h"]))
    add("    <p>%s</p>" % art["cta_p"])
    add('    <a href="/netune-free-beta.html">Download the free beta</a>')
    add("  </div>")
    return "\n".join(out)


def schema(art):
    url = BASE + art["slug"]
    hub = BASE + HUB
    faq = ",\n".join(
        '    { "@type": "Question", "name": %s,\n'
        '      "acceptedAnswer": { "@type": "Answer", "text": %s } }'
        % (jsonstr(item["q"]), jsonstr(plain(item["a"]))) for item in art["faq"])
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": art["h1"], "description": art["meta"],
        "keywords": art["keywords"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": "https://dataash.de/og.png",
        "author": {"@type": "Organization", "name": "DataAsh", "url": BASE},
        "publisher": {"@type": "Organization", "name": "DataAsh", "url": BASE},
        "inLanguage": "en-GB",
        "isPartOf": {"@type": "WebPage", "@id": hub},
    }
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Netune", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Data warehouse methodologies", "item": hub},
            {"@type": "ListItem", "position": 3, "name": art["crumb"], "item": url},
        ],
    }
    tag = '<script type="application/ld+json">\n%s\n</script>'
    return "\n\n".join([
        tag % json.dumps(article, indent=2, ensure_ascii=False),
        tag % ('{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n'
               '  "mainEntity": [\n%s\n  ]\n}' % faq),
        tag % json.dumps(crumbs, indent=2, ensure_ascii=False),
    ])


def render(art, all_articles):
    return _gen.TEMPLATE % {
        "title": esc(art["title"]),
        "meta": esc(art["meta"]),
        "url": BASE + art["slug"],
        "keywords": esc(art["keywords"]),
        "h1": esc(art["h1"]),
        "short_title": esc(art["short"]),
        "tw": esc(art["tw"]),
        "style": STYLE + EXTRA_STYLE,
        "hub": HUB,
        "body": body(art, all_articles),
        "schema": schema(art),
    }


def main():
    from articles import ARTICLES
    for art in ARTICLES:
        html = render(art, ARTICLES)
        with io.open(os.path.join(SITE, art["slug"]), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("  wrote %-34s %6d bytes, %4d words"
              % (art["slug"], len(html), len(plain(html).split())))
    print("wrote %d article(s)" % len(ARTICLES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
