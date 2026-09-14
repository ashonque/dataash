"""Write the eight per-methodology pages from one template.

    python build-methodology-pages.py

Each page goes deep on one methodology - what it is, how the tables are
really shaped, when it fits, when it does not, what it costs, the mistakes
that are expensive, and how it compares with the two or three it is usually
confused with. They exist because that is what somebody types into a search
box: not "data warehouse design" but "kimball vs data vault" or "what is a
satellite in data vault".

**Why generated rather than eight hand-written files.** The head, the schema
blocks, the breadcrumbs, the styles and the cross-links between the eight are
the same on every page, and eight copies of them is eight chances for one to
drift - a canonical pointing at the wrong slug, a breadcrumb naming a page
that was renamed, a sibling link that goes nowhere. Here the content is data
and the shape is written once. Adding a ninth methodology is a ninth entry.

**The "when it fits" and "when it does not" lists are Netune's own.** They are
copied from `GOOD_WHEN` and `POOR_WHEN` in the matching
`methodologies/<id>.py`, and the cost table from that file's `COST`, so the
site and the tool say the same thing about each methodology. If a rule file's
judgement changes, change it here too - the check at the bottom of this file
prints what to compare, but it cannot read the Netune repository from here.
"""
import io
import json
import os
import re

SITE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dataash.de/"
HUB = "data-warehouse-methodologies.html"
DECISIONS = [
    ("kimball-vs-data-vault.html", "Kimball vs Data Vault", "how to choose, and why it is usually both"),
    ("scd-type-1-vs-type-2.html", "SCD type 1 vs type 2", "one dimension at a time"),
    ("what-is-a-staging-layer.html", "What a staging layer is for", "and the four things it must never do"),
]

# The hub page's tokens and rules, kept here rather than shared through a
# stylesheet: a page that carries its own styles cannot be broken by an edit
# made for a different page, and there is no build step to keep in step.
STYLE = """
    :root {
      --navy-900: #0C1B36;
      --navy-700: #1E3A6B;
      --navy-500: #3E68AE;
      --navy-100: #D7E0F0;
      --navy-050: #EDF2FA;
      --ground:   #F7F3EA;
      --surface:  #FFFFFF;
      --ink:      #0C1B36;
      --ink-dim:  #5A6A86;
      --line:     #E3DCCE;
      --ok:       #1F7A4D;
      --no:       #9A3B2F;
      --radius:   14px;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0; background: var(--ground); color: var(--ink);
      font-family: Inter, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 17px; line-height: 1.68; -webkit-font-smoothing: antialiased;
    }
    .wrap { max-width: 760px; margin: 0 auto; padding: 0 24px; }
    header.top {
      border-bottom: 1px solid var(--line); background: var(--ground);
      position: sticky; top: 0; z-index: 10;
    }
    header.top .wrap {
      display: flex; align-items: center; justify-content: space-between;
      padding-top: 16px; padding-bottom: 16px;
    }
    .brand {
      font-weight: 800; font-size: 19px; color: var(--navy-700);
      text-decoration: none; letter-spacing: -0.01em;
    }
    .brand span { color: var(--navy-500); font-weight: 500; }
    .top a.back { font-size: 14px; color: var(--ink-dim); text-decoration: none; }
    .top a.back:hover { color: var(--navy-700); }

    nav.crumbs { font-size: 13px; color: var(--ink-dim); padding: 22px 0 0; }
    nav.crumbs a { color: var(--navy-500); text-decoration: none; }
    nav.crumbs a:hover { text-decoration: underline; }

    h1 {
      font-size: clamp(29px, 5vw, 42px); line-height: 1.14;
      letter-spacing: -0.02em; margin: 14px 0 8px;
    }
    .also { font-size: 14px; color: var(--ink-dim); margin: 0 0 16px; }
    .standfirst { font-size: 20px; color: var(--ink-dim); margin: 0 0 30px; }
    h2 {
      font-size: clamp(22px, 3.4vw, 27px); line-height: 1.25;
      letter-spacing: -0.01em; margin: 48px 0 12px; scroll-margin-top: 80px;
    }
    h3 { font-size: 18.5px; margin: 28px 0 8px; }
    p { margin: 0 0 18px; }
    ul, ol { margin: 0 0 18px; padding-left: 22px; }
    li { margin-bottom: 9px; }
    strong { color: var(--navy-900); }
    a { color: var(--navy-700); }
    code {
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 0.88em; background: var(--navy-050);
      padding: 2px 6px; border-radius: 5px; color: var(--navy-700);
    }
    pre {
      background: var(--navy-900); color: #E8EEF9; border-radius: var(--radius);
      padding: 16px 18px; overflow-x: auto; font-size: 13.5px; line-height: 1.6;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }
    pre code { background: none; color: inherit; padding: 0; font-size: inherit; }

    .fits {
      display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 22px 0;
    }
    .fits > div {
      background: var(--surface); border: 1px solid var(--line);
      border-radius: var(--radius); padding: 4px 20px 14px;
    }
    .fits .yes { border-top: 3px solid var(--ok); }
    .fits .no  { border-top: 3px solid var(--no); }
    .fits h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .09em; margin: 16px 0 10px; }
    .fits .yes h3 { color: var(--ok); }
    .fits .no h3  { color: var(--no); }
    .fits ul { padding-left: 20px; margin: 0; font-size: 15.5px; }
    @media (max-width: 620px) { .fits { grid-template-columns: 1fr; } }

    .wide { overflow-x: auto; margin: 22px 0; }
    table {
      width: 100%; border-collapse: collapse; font-size: 15px;
      background: var(--surface); border: 1px solid var(--line);
      border-radius: var(--radius); overflow: hidden; min-width: 480px;
    }
    th, td { text-align: left; padding: 11px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
    th { background: var(--navy-050); font-weight: 600; color: var(--navy-700); }
    tr:last-child td { border-bottom: none; }

    .note {
      background: var(--surface); border: 1px solid var(--line);
      border-left: 4px solid var(--navy-500);
      border-radius: var(--radius); padding: 18px 22px; margin: 26px 0;
    }
    .note p:last-child { margin-bottom: 0; }

    .faq-item { border-bottom: 1px solid var(--line); padding: 18px 0; }
    .faq-item h3 { margin: 0 0 6px; font-size: 17.5px; }
    .faq-item p { margin: 0; color: var(--ink-dim); }

    .siblings { margin: 44px 0 0; }
    .siblings ul {
      list-style: none; padding: 0; display: grid;
      grid-template-columns: 1fr 1fr; gap: 10px;
    }
    .siblings li { margin: 0; }
    .siblings a {
      display: block; background: var(--surface); border: 1px solid var(--line);
      border-radius: 10px; padding: 11px 14px; text-decoration: none;
      font-size: 15px; font-weight: 600;
    }
    .siblings a:hover { border-color: var(--navy-500); }
    .siblings a span { display: block; font-weight: 400; font-size: 13.5px; color: var(--ink-dim); }
    @media (max-width: 620px) { .siblings ul { grid-template-columns: 1fr; } }

    .cta {
      background: var(--navy-700); color: #fff; border-radius: var(--radius);
      padding: 32px; margin: 48px 0 20px;
    }
    .cta h2 { margin: 0 0 10px; color: #fff; }
    .cta p { color: var(--navy-100); margin-bottom: 20px; }
    .cta a {
      display: inline-block; background: #fff; color: var(--navy-700);
      padding: 13px 24px; border-radius: 10px; text-decoration: none;
      font-weight: 700; font-size: 15px;
    }
    .cta a:hover { background: var(--navy-050); }

    footer { border-top: 1px solid var(--line); margin-top: 52px; padding: 26px 0 46px; }
    footer .wrap { font-size: 14px; color: var(--ink-dim); }
    footer a { color: var(--navy-700); }
    @media (max-width: 560px) {
      body { font-size: 16px; }
      .cta { padding: 24px; }
      /* the header's two items cannot both fit on a phone, and the breadcrumb
         immediately below goes to the same place */
      header.top a.back { display: none; }
    }
"""


def esc(text):
    """The few characters that cannot travel as themselves inside markup."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def jsonstr(text):
    """A JSON string, so a quote or a dash in the prose cannot break the schema."""
    return json.dumps(text, ensure_ascii=False)


def plain(html):
    """Markup out, words in - what the schema block needs.

    A FAQ answer is written once, with its links, and has to appear twice: on
    the page as markup and in the JSON-LD as text. Writing it twice is how the
    two come to disagree, and the copy search engines read is the one nobody
    ever looks at.
    """
    # a <style> or <script> block's contents are not prose, and counting them
    # would flatter every page by a couple of thousand words
    text = html
    for tag in ("style", "script"):
        text = re.sub("<%s[^>]*>.*?</%s>" % (tag, tag), " ", text,
                      flags=re.S | re.I)
    text = re.sub("<[^>]+>", "", text)
    for entity, char in (("&mdash;", "-"), ("&nbsp;", " "), ("&rsquo;", "'"),
                         ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")):
        text = text.replace(entity, char)
    return re.sub(r"\s+", " ", text).strip()


def sections(page):
    """The page body, section by section, as a list of markup lines."""
    out = []
    add = out.append

    add('  <nav class="crumbs" aria-label="Breadcrumb">')
    add('    <a href="/">Netune</a> &rsaquo; '
        '<a href="/%s">Data warehouse methodologies</a> &rsaquo; %s' % (HUB, esc(page["crumb"])))
    add('  </nav>')
    add("  <h1>%s</h1>" % esc(page["h1"]))
    add('  <p class="also">Also called: %s</p>' % esc(page["also"]))
    add('  <p class="standfirst">%s</p>' % page["standfirst"])

    add('  <h2 id="what">What it is</h2>')
    for para in page["what"]:
        add("  <p>%s</p>" % para)

    add('  <h2 id="shape">How the tables are actually shaped</h2>')
    for part in page["shape"]:
        if part.get("h3"):
            add("  <h3>%s</h3>" % esc(part["h3"]))
        for para in part.get("body", []):
            add("  <p>%s</p>" % para)
        if part.get("code"):
            add("  <pre><code>%s</code></pre>" % esc(part["code"]))
        # "after" is the same as "body" on the far side of the code block, for
        # a section whose explanation only makes sense once you have seen it
        for para in part.get("after", []):
            add("  <p>%s</p>" % para)
        if part.get("list"):
            add("  <ul>")
            for item in part["list"]:
                add("    <li>%s</li>" % item)
            add("  </ul>")

    add('  <h2 id="fit">When it fits, and when it does not</h2>')
    add("  <p>%s</p>" % page["fit_intro"])
    add('  <div class="fits">')
    add('    <div class="yes"><h3>It fits when</h3><ul>')
    for item in page["good_when"]:
        add("      <li>%s</li>" % esc(item))
    add("    </ul></div>")
    add('    <div class="no"><h3>It fits badly when</h3><ul>')
    for item in page["poor_when"]:
        add("      <li>%s</li>" % esc(item))
    add("    </ul></div>")
    add("  </div>")
    add('  <p class="also">Those two lists are Netune&rsquo;s own judgement of this '
        'methodology, copied from the rule file it scores a real database with.</p>')

    add('  <h2 id="cost">What it costs</h2>')
    add('  <div class="wide">')
    add("    <table>")
    add("      <thead><tr><th>&nbsp;</th><th>Cost</th><th>What that means here</th></tr></thead>")
    add("      <tbody>")
    for label, verdict, why in page["cost"]:
        add("        <tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>"
            % (esc(label), esc(verdict), why))
    add("      </tbody>")
    add("    </table>")
    add("  </div>")

    add('  <h2 id="mistakes">The mistakes that are expensive</h2>')
    for item in page["mistakes"]:
        add("  <h3>%s</h3>" % esc(item["h3"]))
        for para in item["body"]:
            add("  <p>%s</p>" % para)

    add('  <h2 id="versus">How it compares</h2>')
    for item in page["versus"]:
        add("  <h3>%s</h3>" % esc(item["h3"]))
        for para in item["body"]:
            add("  <p>%s</p>" % para)

    add('  <div class="note">')
    add("    <p>%s</p>" % page["netune_note"])
    add("  </div>")

    add('  <h2 id="faq">Questions people ask</h2>')
    add('  <section class="faq">')
    for item in page["faq"]:
        add('    <div class="faq-item">')
        add("      <h3>%s</h3>" % esc(item["q"]))
        add("      <p>%s</p>" % item["a"])
        add("    </div>")
    add("  </section>")

    return out


def siblings(page, others):
    """Every page links to every other, so none of the eight is a dead end."""
    out = ['  <section class="siblings">', "    <h2>The other seven</h2>", "    <ul>"]
    for other in others:
        if other["slug"] == page["slug"]:
            continue
        out.append('      <li><a href="/%s">%s<span>%s</span></a></li>'
                   % (other["slug"], esc(other["short"]), esc(other["oneline"])))
    out.append("    </ul>")
    out.append('    <p style="margin-top:16px"><a href="/%s">'
               "&larr; All eight compared, and how to choose between them</a></p>" % HUB)
    out.append("  </section>")
    # the decision articles are relevant on every one of the eight, so they are
    # listed on every one rather than tuned per page and forgotten on some
    out.append('  <section class="siblings">')
    out.append("    <h2>Deciding between them</h2>")
    out.append("    <ul>")
    for slug, label, why in DECISIONS:
        out.append('      <li><a href="/%s">%s<span>%s</span></a></li>' % (slug, esc(label), esc(why)))
    out.append("    </ul>")
    out.append("  </section>")
    out.append('  <div class="cta">')
    out.append("    <h2>%s</h2>" % esc(page["cta_h"]))
    out.append("    <p>%s</p>" % page["cta_p"])
    out.append('    <a href="/netune-free-beta.html">Download the free beta</a>')
    out.append("  </div>")
    return out


def schema_for(page):
    """Article, FAQPage and BreadcrumbList, built from the page's own words."""
    url = BASE + page["slug"]
    hub = BASE + HUB
    faq = ",\n".join(
        '    { "@type": "Question", "name": %s,\n'
        '      "acceptedAnswer": { "@type": "Answer", "text": %s } }'
        % (jsonstr(item["q"]), jsonstr(plain(item["a"]))) for item in page["faq"])

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": page["h1"],
        "description": page["meta"],
        "about": {"@type": "Thing", "name": page["thing"]},
        "keywords": page["keywords"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": "https://dataash.de/og.png",
        "author": {"@type": "Organization", "name": "DataAsh", "url": "https://dataash.de/"},
        "publisher": {"@type": "Organization", "name": "DataAsh", "url": "https://dataash.de/"},
        "inLanguage": "en-GB",
        "isPartOf": {"@type": "WebPage", "@id": hub},
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Netune", "item": BASE},
            {"@type": "ListItem", "position": 2,
             "name": "Data warehouse methodologies", "item": hub},
            {"@type": "ListItem", "position": 3, "name": page["crumb"], "item": url},
        ],
    }
    block = '<script type="application/ld+json">\n%s\n</script>'
    return "\n\n".join([
        block % json.dumps(article, indent=2, ensure_ascii=False),
        block % ('{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n'
                 '  "mainEntity": [\n%s\n  ]\n}' % faq),
        block % json.dumps(crumbs, indent=2, ensure_ascii=False),
    ])


def render(page, others):
    url = BASE + page["slug"]
    body = "\n".join(sections(page) + [""] + siblings(page, others))
    return TEMPLATE % {
        "title": esc(page["title"]),
        "meta": esc(page["meta"]),
        "url": url,
        "keywords": esc(page["keywords"]),
        "h1": esc(page["h1"]),
        "short_title": esc(page["short_title"]),
        "tw": esc(page["tw"]),
        "style": STYLE,
        "hub": HUB,
        "body": body,
        "schema": schema_for(page),
    }


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script src="/analytics.js" defer></script>
  <title>%(title)s</title>
  <meta name="description" content="%(meta)s" />
  <link rel="canonical" href="%(url)s" />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large" />
  <meta name="keywords" content="%(keywords)s" />

  <meta property="og:type" content="article" />
  <meta property="og:title" content="%(h1)s" />
  <meta property="og:description" content="%(meta)s" />
  <meta property="og:url" content="%(url)s" />
  <meta property="og:site_name" content="Netune" />
  <meta property="og:image" content="https://dataash.de/og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:locale" content="en_GB" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="%(short_title)s" />
  <meta name="twitter:description" content="%(tw)s" />
  <meta name="twitter:image" content="https://dataash.de/og.png" />

  <meta name="theme-color" content="#1E3A6B" />
  <link rel="icon" href="/favicon.ico?v=2" sizes="16x16 32x32 48x48" />
  <link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400..800&display=swap" rel="stylesheet" />

  <style>%(style)s  </style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <a class="brand" href="/">Netune<span> by DataAsh</span></a>
    <a class="back" href="/%(hub)s">&larr; All eight methodologies</a>
  </div>
</header>

<main class="wrap">
%(body)s
</main>

<footer>
  <div class="wrap">
    &copy; 2026 DataAsh &middot; <a href="/">Netune</a> &middot;
    <a href="/%(hub)s">Choose a model</a> &middot;
    <a href="/netune-free-beta.html">Free beta</a> &middot;
    <a href="mailto:dataash@proton.me">dataash@proton.me</a>
  </div>
</footer>

%(schema)s

</body>
</html>
"""


def main():
    from methodology_pages import PAGES
    for page in PAGES:
        html = render(page, PAGES)
        path = os.path.join(SITE, page["slug"])
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("  wrote %-42s %6d bytes, %4d words"
              % (page["slug"], len(html), len(plain(html).split())))
    print("wrote %d page(s)" % len(PAGES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
