"""Deploy netune-stats to Cloudflare, with nothing installed but Python.

    set CF_API_TOKEN and GH_TOKEN in your own terminal, then:
    python worker\\deploy.py            # create or update everything, then commit the URL
    python worker\\deploy.py --no-push  # the same, but leave the commit to you

Cloudflare's own tool, wrangler, needs Node.js, and this machine has not
got it. Everything wrangler would do is a handful of REST calls, so they
are made here directly: find the account, create the D1 database if it is
missing and apply schema.sql, upload index.js with the database bound as
DB, store the GitHub token as the Worker's secret, switch on the
workers.dev address, and check it answers. Then the address is written
where the two things that need it will find it - stats/api.txt for the
nightly Action and the beta page's API constant - and committed.

**Two tokens, both made by you, both pasted only into your own terminal.**

  CF_API_TOKEN  Cloudflare > My Profile > API Tokens > Create Token >
                "Create Custom Token", with these three permissions:
                   Account | Workers Scripts | Edit
                   Account | D1             | Edit
                   Account | Account Settings | Read
                Nothing else. It is used only while this script runs and
                is never written anywhere.

  GH_TOKEN      GitHub > Settings > Developer settings > Personal access
                tokens > Fine-grained > Generate: repository access ONLY
                ashonque/dataash, permission Contents: Read and write.
                This one is handed to the Worker as its secret, because
                the Worker is what appends to feedback/feedback.txt. If it
                ever leaked, the worst it could do is edit that one
                repository. Set an expiry and note the date.

Run again whenever index.js or schema.sql changes; every step is idempotent.
"""
import json
import mimetypes
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
NAME = "netune-stats"
DB_NAME = "netune-stats"
COMPAT = "2025-09-01"
API = "https://api.cloudflare.com/client/v4"

CF = os.environ.get("CF_API_TOKEN", "").strip()
GH = os.environ.get("GH_TOKEN", "").strip()


def die(msg):
    print("\n  !! " + msg)
    sys.exit(1)


def cf(path, method="GET", body=None, raw=None, ctype=None):
    headers = {"Authorization": "Bearer " + CF}
    data = None
    if raw is not None:
        data, headers["Content-Type"] = raw, ctype
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            out = json.loads(e.read() or b"{}")
        except ValueError:
            out = {"success": False, "errors": [{"message": "HTTP %d" % e.code}]}
        out.setdefault("success", False)
        out["_status"] = e.code
    return out


def must(out, doing):
    if not out.get("success"):
        errs = "; ".join(str(e.get("message", e)) for e in out.get("errors", [])) or str(out)
        die("Cloudflare refused while %s: %s" % (doing, errs))
    return out.get("result")


def multipart(parts):
    """(bytes, content-type) for a multipart/form-data body."""
    boundary = "----netune" + uuid.uuid4().hex
    out = bytearray()
    for name, filename, ctype, content in parts:
        out += ("--%s\r\n" % boundary).encode()
        out += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (name, filename)).encode()
        out += ("Content-Type: %s\r\n\r\n" % ctype).encode()
        out += content if isinstance(content, bytes) else content.encode("utf-8")
        out += b"\r\n"
    out += ("--%s--\r\n" % boundary).encode()
    return bytes(out), "multipart/form-data; boundary=" + boundary


def main(argv):
    push = "--no-push" not in argv
    if not CF:
        die("CF_API_TOKEN is not set. In PowerShell:  $env:CF_API_TOKEN = \"...\"   (see the notes at the top of this file)")
    if not GH:
        die("GH_TOKEN is not set. In PowerShell:  $env:GH_TOKEN = \"...\"   (a fine-grained token for ashonque/dataash, Contents: read and write)")

    print("== the account ==")
    accounts = must(cf("/accounts?per_page=5"), "listing accounts")
    if not accounts:
        die("The token can see no account. It needs 'Account Settings: Read'.")
    acct = accounts[0]["id"]
    print("  " + accounts[0].get("name", acct))

    print("\n== the database ==")
    found = must(cf("/accounts/%s/d1/database?name=%s" % (acct, DB_NAME)), "looking for the database")
    found = [d for d in (found or []) if d.get("name") == DB_NAME]
    if found:
        db = found[0]["uuid"]
        print("  %s exists" % DB_NAME)
    else:
        db = must(cf("/accounts/%s/d1/database" % acct, "POST", {"name": DB_NAME}), "creating the database")["uuid"]
        print("  %s created" % DB_NAME)
    with open(os.path.join(HERE, "schema.sql"), encoding="utf-8") as f:
        schema = f.read()
    for stmt in [s.strip() for s in re.sub(r"--[^\n]*", "", schema).split(";") if s.strip()]:
        must(cf("/accounts/%s/d1/database/%s/query" % (acct, db), "POST", {"sql": stmt + ";"}), "applying the schema")
    print("  schema applied")

    print("\n== the worker ==")
    with open(os.path.join(HERE, "index.js"), encoding="utf-8") as f:
        script = f.read()
    metadata = {
        "main_module": "index.js",
        "compatibility_date": COMPAT,
        "bindings": [{"type": "d1", "name": "DB", "id": db}],
        "keep_bindings": ["secret_text"],
    }
    body, ctype = multipart([
        ("metadata", "metadata.json", "application/json", json.dumps(metadata)),
        ("index.js", "index.js", "application/javascript+module", script),
    ])
    must(cf("/accounts/%s/workers/scripts/%s" % (acct, NAME), "PUT", raw=body, ctype=ctype), "uploading the script")
    print("  %s uploaded" % NAME)
    must(cf("/accounts/%s/workers/scripts/%s/secrets" % (acct, NAME), "PUT",
            {"name": "GITHUB_TOKEN", "text": GH, "type": "secret_text"}), "storing the GitHub token as a secret")
    print("  GITHUB_TOKEN stored as a secret")

    print("\n== the address ==")
    sub = cf("/accounts/%s/workers/subdomain" % acct)
    subdomain = (sub.get("result") or {}).get("subdomain") if sub.get("success") else None
    if not subdomain:
        # the account has never chosen one; take a sensible name, or a unique one
        for candidate in ["dataash", "dataash-" + acct[:6]]:
            made = cf("/accounts/%s/workers/subdomain" % acct, "PUT", {"subdomain": candidate})
            if made.get("success"):
                subdomain = made["result"]["subdomain"]
                break
        if not subdomain:
            die("Could not choose a workers.dev subdomain; open Workers & Pages in the Cloudflare dashboard once, pick one, and run this again.")
    must(cf("/accounts/%s/workers/scripts/%s/subdomain" % (acct, NAME), "POST",
            {"enabled": True, "previews_enabled": False}), "switching on the workers.dev address")
    url = "https://%s.%s.workers.dev" % (NAME, subdomain)
    print("  " + url)

    print("\n== does it answer ==")
    ok = False
    for _ in range(12):
        try:
            with urllib.request.urlopen(url + "/counts", timeout=20) as r:
                got = json.loads(r.read())
            ok = bool(got.get("ok"))
            break
        except Exception:
            time.sleep(5)
    if not ok:
        die("The worker is deployed but %s/counts did not answer yet. Wait a minute and open it in a browser; if it still fails, run this again." % url)
    print("  /counts -> ok, totals: " + json.dumps(got.get("total")))
    # a refusal that proves the checks run, without writing anything
    req = urllib.request.Request(url + "/feedback", data=json.dumps({"text": "word " * 60}).encode(),
                                 headers={"Content-Type": "application/json", "Origin": "https://dataash.de"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=20)
        die("A 60-word submission was accepted; the word limit is not being applied.")
    except urllib.error.HTTPError as e:
        print("  /feedback refuses 60 words -> %d %s" % (e.code, json.loads(e.read()).get("error", "")))

    print("\n== telling the site ==")
    with open(os.path.join(SITE, "stats", "api.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(url + "\n")
    page = os.path.join(SITE, "netune-free-beta.html")
    with open(page, encoding="utf-8") as f:
        html = f.read()
    new_html, n = re.subn(r'var API = "[^"]*";', 'var API = "%s";' % url, html)
    if n != 1:
        die("Could not find the API constant in netune-free-beta.html.")
    if new_html != html:
        with open(page, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_html)
    print("  stats/api.txt and the beta page name " + url)

    if push:
        run = lambda *a: subprocess.run(["git"] + list(a), cwd=SITE, capture_output=True, text=True)
        run("add", "stats/api.txt", "netune-free-beta.html")
        if run("diff", "--cached", "--quiet").returncode != 0:
            run("commit", "-q", "-m", "Point the beta page and the nightly count at the worker")
            out = run("push", "origin", "main")
            print("  committed and pushed" if out.returncode == 0 else "  commit made; push failed:\n" + out.stderr)
        else:
            print("  nothing new to commit")

    print("\nDone. The counters and the feedback box are live at " + url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
