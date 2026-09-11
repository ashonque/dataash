"""Append today's download count to stats/downloads.txt.

    python stats/count-downloads.py            # writes the line, prints it
    python stats/count-downloads.py --check    # prints it, writes nothing

GitHub counts every download of a release asset itself - a browser click on
the page, the one-line installer, curl, all of them - and publishes it as
`download_count` on the release. That is the ground truth for "how many
people downloaded Netune", and nothing on the website could count it better:
a click on the Download button is an intention, and the file leaving GitHub
is the fact.

So this reads that number and writes it down, once a day, from a GitHub
Action (see .github/workflows/downloads.yml). Three decisions:

**The file is appended, never rewritten**, so it is a history: one line per
day the total moved, oldest first. A day with no line had no downloads.

**A line is written only when the total changed.** Every commit to `main`
rebuilds the website, and a commit that says "nothing happened" is a rebuild
for nothing.

**Every release is counted, and named.** When 1.0.1 ships, its zip appears
beside 1.0.0's on the same line, and the total is the total.

The `.sha256` files beside the zips are not counted: the installer fetches
nothing but the zip, and a checksum download is not a Netune download.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

REPO = "ashonque/dataash"
HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "downloads.txt")

HEADER = """# Netune downloads, counted by GitHub on the release assets.
# One line per day the total changed, oldest first; a day with no line had
# no downloads. Written by stats/count-downloads.py from a nightly Action.
#
# date        total   today   per release                 |  what the page counted
"""


def releases():
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/releases?per_page=100" % REPO,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "netune-stats",
                 **({"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]}
                    if os.environ.get("GITHUB_TOKEN") else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def counts():
    """{release tag: downloads of its zip(s)}, oldest release first."""
    out = {}
    for rel in sorted(releases(), key=lambda r: r.get("created_at") or ""):
        n = sum(a.get("download_count") or 0 for a in rel.get("assets") or []
                if a.get("name", "").lower().endswith(".zip"))
        out[rel.get("tag_name") or "?"] = n
    return out


def clicks():
    """What the page's own counters say - copy buttons and download clicks -
    from the worker named in stats/api.txt, once it has been deployed.
    Intentions, beside the downloads that are facts; absent, the line is
    just shorter."""
    where = os.path.join(HERE, "api.txt")
    if not os.path.exists(where):
        return ""
    with open(where, encoding="utf-8") as f:
        api = f.read().strip().rstrip("/")
    if not api:
        return ""
    try:
        req = urllib.request.Request(api + "/counts", headers={"User-Agent": "netune-stats"})
        with urllib.request.urlopen(req, timeout=30) as r:
            got = json.loads(r.read()).get("total") or {}
    except Exception as e:
        print("  (the click counter did not answer: %s)" % e)
        return ""
    return "clicks %d  copies ps %d cmd %d  feedback %d" % (
        got.get("download_click", 0), got.get("copy_ps", 0), got.get("copy_cmd", 0), got.get("feedback", 0))


def last_total(text):
    """The total on the newest line, or 0 when the file is new."""
    total = 0
    for line in text.splitlines():
        m = re.match(r"\d{4}-\d{2}-\d{2}\s+(\d+)\s+", line)
        if m:
            total = int(m.group(1))
    return total


def main(argv):
    check = "--check" in argv
    existing = ""
    if os.path.exists(FILE):
        with open(FILE, encoding="utf-8") as f:
            existing = f.read()

    per = counts()
    total = sum(per.values())
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    # a line already written today (the Action re-run by hand) is replaced
    # rather than repeated, and "today" is then counted from the day before
    kept = [ln for ln in existing.splitlines() if not ln.startswith(today + "  ")]
    before = last_total("\n".join(kept))
    extra = clicks()
    line = "%s  %6d  %6d   %s%s" % (today, total, total - before,
                                    "  ".join("%s %d" % kv for kv in per.items()),
                                    ("   |  " + extra) if extra else "")
    print(line)

    # the download total is what decides whether a day gets a line; the
    # click counts ride along on it rather than earning commits of their own
    if existing and total == last_total(existing):
        print("unchanged since the last line; nothing written")
        return 0
    if check:
        return 0

    body = "\n".join(kept).rstrip("\n")
    if not body.startswith("#"):
        body = HEADER.rstrip("\n") + ("\n" + body if body else "")
    with open(FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(body + "\n" + line + "\n")
    print("wrote " + os.path.relpath(FILE, os.getcwd()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
