"""Write sitemap.xml from the pages that are really here.

A sitemap is a claim about a site, and the only failure that matters is the
claim going quietly out of date: a page added and not listed, a page deleted
and still listed, a `lastmod` that has said the same thing for a year. Every
one of those is a hand-maintained file's ordinary fate, which is why this is
generated rather than edited.

    python build-sitemap.py

Two decisions worth stating.

**Only <loc> and <lastmod> are written.** Google ignores <priority> and
<changefreq> and says so plainly, and Bing gives priority almost no weight.
They were in this file for years and did nothing. Leaving them in is not
harmful, but it invites the next person to tune numbers that are read by
nobody, which is worse than an empty field.

**<lastmod> comes from git, not from a judgement.** Google's own guidance is
that it should reflect the last *significant* change - and "was that
significant?" is a question that gets asked carefully twice and then stops
being asked at all. The date of the last commit that touched the file is a
fact instead, and a fact can be checked. If a change really is cosmetic, the
honest response is to not regenerate rather than to write a date that is not
true. What Google penalises is a sitemap that stamps today on every URL every
time it is fetched; this is the opposite of that.

**A page that says noindex is never listed.** 404.html asks not to be indexed,
so listing it would be the sitemap contradicting the page - and when a sitemap
and a page disagree, the page wins and the sitemap is what stops being
trusted. The rule is read from each file rather than kept as a list here.
"""
import os
import re
import subprocess
import sys
from datetime import date

SITE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dataash.de/"
GIT = r"C:\Program Files\Git\cmd\git.exe"

# the home page is served at the bare address, not at its file name
AS_ROOT = "index.html"


def indexable(name):
    """Does this page ask to be indexed? Asked of the page, not assumed."""
    with open(os.path.join(SITE, name), encoding="utf-8") as f:
        head = f.read(4000)
    tag = re.search(r'<meta\s+name="robots"\s+content="([^"]*)"', head, re.I)
    return not (tag and "noindex" in tag.group(1).lower())


def last_changed(name):
    """The date of the last commit that touched this file."""
    try:
        out = subprocess.run([GIT, "log", "-1", "--format=%cs", "--", name],
                             cwd=SITE, capture_output=True, text=True, timeout=60)
        stamp = (out.stdout or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
            return stamp
    except (OSError, subprocess.SubprocessError):
        pass
    # never committed yet, or no git here: the file's own date is still true
    return date.fromtimestamp(os.path.getmtime(os.path.join(SITE, name))).isoformat()


def pages():
    out = []
    for name in sorted(os.listdir(SITE)):
        if not name.lower().endswith(".html"):
            continue
        if not indexable(name):
            print("  skipped %-26s it asks not to be indexed" % name)
            continue
        where = BASE if name == AS_ROOT else BASE + name
        out.append((where, last_changed(name)))
    # the home page first, then the rest by address, so a diff of this file
    # is readable rather than reordered
    out.sort(key=lambda row: (row[0] != BASE, row[0]))
    return out


def main():
    found = pages()
    if not found:
        print("no indexable pages found - refusing to write an empty sitemap")
        return 1

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for where, when in found:
        lines += ["", "  <url>",
                  "    <loc>%s</loc>" % where,
                  "    <lastmod>%s</lastmod>" % when,
                  "  </url>"]
    lines += ["", "</urlset>", ""]

    path = os.path.join(SITE, "sitemap.xml")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    for where, when in found:
        print("  listed  %-46s %s" % (where, when))
    print("wrote sitemap.xml with %d url(s)" % len(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
