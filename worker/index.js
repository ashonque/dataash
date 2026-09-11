/* netune-stats - the small server behind dataash.de's counters and feedback.
 *
 * A static site cannot write to its own repository: whatever holds the
 * GitHub token has to be somewhere a browser cannot read, and this is it. It
 * runs as a Cloudflare Worker with a D1 database, and answers four things:
 *
 *   POST /count       body: copy_ps | copy_cmd | download_click
 *                     +1 to that event for today. No cookie, no IP, nothing
 *                     stored but the number - so no consent is needed.
 *   GET  /counts      the totals, as JSON. The nightly GitHub Action reads
 *                     this and writes it into stats/downloads.txt.
 *   POST /feedback    JSON {text, page, website}. At most 50 words, no links,
 *                     one per address per ten minutes, a hundred a day in
 *                     all. Appended to feedback/feedback.txt in the
 *                     repository - oldest first, because appending is
 *                     ascending - and kept here too in case GitHub is down
 *                     at that moment; the next submission flushes the queue.
 *   GET  /feedback    the newest few accepted lines, so the page can show
 *                     that the box is real.
 *
 * What is deliberately not here: no IP address is ever written down. The
 * rate limit keys on a hash of the address and the day that lives for a
 * day and is then deleted. No names, no e-mail, no account. The feedback
 * file is public and the page says so before anybody types.
 *
 * Deployed by worker/deploy.py; the GitHub token is a Worker secret.
 */

const REPO = "ashonque/dataash";
const FILE = "feedback/feedback.txt";
const ALLOWED_ORIGINS = ["https://dataash.de", "https://www.dataash.de"];
const EVENTS = ["copy_ps", "copy_cmd", "download_click"];
const MAX_WORDS = 50;
const MAX_CHARS = 400;
const PER_ADDRESS_SECONDS = 600;
const PER_DAY = 100;

const FILE_HEADER =
  "# Feedback on the Netune free beta, left through https://dataash.de/netune-free-beta.html\n" +
  "# One line each, oldest first, as written - at most fifty words, no links, no names asked for.\n" +
  "#\n";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsFor(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    try {
      if (url.pathname === "/count" && request.method === "POST") {
        return await count(request, env, cors, origin);
      }
      if (url.pathname === "/counts" && request.method === "GET") {
        return json(await totals(env), 200, cors);
      }
      if (url.pathname === "/feedback" && request.method === "POST") {
        return await feedback(request, env, cors, origin);
      }
      if (url.pathname === "/feedback" && request.method === "GET") {
        return json(await recent(env, url.searchParams.get("n")), 200, cors);
      }
      if (url.pathname === "/") {
        return new Response("netune-stats: /counts, /feedback", { headers: cors });
      }
      return json({ ok: false, error: "No such thing here." }, 404, cors);
    } catch (e) {
      return json({ ok: false, error: "Something went wrong on our side: " + (e && e.message) }, 500, cors);
    }
  },
};

/* ---------------------------------------------------------------- helpers */
function corsFor(origin) {
  const h = { "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
  if (ALLOWED_ORIGINS.includes(origin)) {
    h["Access-Control-Allow-Origin"] = origin;
    h["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
    h["Access-Control-Allow-Headers"] = "Content-Type";
    h["Access-Control-Max-Age"] = "86400";
    h["Vary"] = "Origin";
  }
  return h;
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign({ "Content-Type": "application/json; charset=utf-8" }, headers),
  });
}

function fromOurPage(origin) {
  // a browser sends Origin on every cross-site POST and cannot forge it; a
  // script can, and the rate limits are what answer a script
  return ALLOWED_ORIGINS.includes(origin);
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

/* ---------------------------------------------------------------- counting */
async function count(request, env, cors, origin) {
  if (!fromOurPage(origin)) return json({ ok: false, error: "Counted only from dataash.de." }, 403, cors);
  const event = (await request.text()).trim().slice(0, 40);
  if (!EVENTS.includes(event)) return json({ ok: false, error: "Not an event we count." }, 400, cors);
  await env.DB.prepare(
    "INSERT INTO counts (event, day, n) VALUES (?, ?, 1) " +
    "ON CONFLICT(event, day) DO UPDATE SET n = n + 1"
  ).bind(event, today()).run();
  return json({ ok: true }, 200, cors);
}

async function totals(env) {
  const rows = (await env.DB.prepare(
    "SELECT event, SUM(n) AS total, SUM(CASE WHEN day = ? THEN n ELSE 0 END) AS today " +
    "FROM counts GROUP BY event"
  ).bind(today()).all()).results || [];
  const out = { ok: true, day: today(), total: {}, today: {} };
  for (const ev of EVENTS) { out.total[ev] = 0; out.today[ev] = 0; }
  for (const r of rows) { out.total[r.event] = r.total; out.today[r.event] = r.today; }
  const fb = await env.DB.prepare("SELECT COUNT(*) AS n FROM feedback WHERE accepted = 1").first();
  out.total.feedback = (fb && fb.n) || 0;
  return out;
}

/* ---------------------------------------------------------------- feedback */
function clean(text) {
  // one line of plain text: no control characters, no runs of space
  return String(text || "")
    .normalize("NFC")
    .replace(/[\u0000-\u001F\u007F\u2028\u2029]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function judge(text) {
  if (!text) return "Write something first.";
  if (text.length > MAX_CHARS) return "That is longer than " + MAX_CHARS + " characters.";
  const words = text.split(" ").filter(Boolean).length;
  if (words > MAX_WORDS) return "That is " + words + " words; the limit is " + MAX_WORDS + ".";
  if (words < 2) return "A word or two more, so it can be understood on its own.";
  if (/https?:\/\/|www\.|\.(com|de|net|org|io|ru|xyz)\b\/?/i.test(text)) return "Links are not accepted here.";
  if (/(.)\1{9,}/.test(text)) return "That does not look like a sentence.";
  return "";
}

async function feedback(request, env, cors, origin) {
  if (!fromOurPage(origin)) return json({ ok: false, error: "Feedback is taken only from dataash.de." }, 403, cors);
  let body;
  try { body = await request.json(); } catch (e) { return json({ ok: false, error: "Send JSON." }, 400, cors); }

  // the honeypot: a field people cannot see and robots fill in
  if (body && body.website) return json({ ok: true, accepted: true }, 200, cors);

  const text = clean(body && body.text);
  const why = judge(text);
  if (why) return json({ ok: false, error: why }, 400, cors);

  // the rate limit, on a hash that names nobody and lives a day
  const ip = request.headers.get("CF-Connecting-IP") || "0";
  const key = await sha256(ip + "|" + today() + "|netune");
  const now = Math.floor(Date.now() / 1000);
  const last = await env.DB.prepare("SELECT at FROM limits WHERE key = ?").bind(key).first();
  if (last && now - last.at < PER_ADDRESS_SECONDS) {
    return json({ ok: false, error: "One piece of feedback every ten minutes, please." }, 429, cors);
  }
  const dayCount = await env.DB.prepare("SELECT COUNT(*) AS n FROM feedback WHERE accepted = 1 AND at >= ?")
    .bind(today() + "T00:00:00Z").first();
  if (dayCount && dayCount.n >= PER_DAY) {
    return json({ ok: false, error: "The box is full for today; please try tomorrow." }, 429, cors);
  }
  await env.DB.batch([
    env.DB.prepare("INSERT INTO limits (key, at) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET at = ?").bind(key, now, now),
    env.DB.prepare("DELETE FROM limits WHERE at < ?").bind(now - 86400),
  ]);

  const at = new Date().toISOString().replace("T", " ").slice(0, 16) + " UTC";
  const page = clean(body && body.page).slice(0, 80);
  await env.DB.prepare("INSERT INTO feedback (at, text, page, accepted, committed) VALUES (?, ?, ?, 1, 0)")
    .bind(new Date().toISOString(), text, page).run();

  // into the repository - this one and anything an earlier failure left behind
  let committed = false;
  try {
    committed = await flush(env);
  } catch (e) {
    committed = false;
  }
  return json({ ok: true, accepted: true, committed, at, text }, 200, cors);
}

async function recent(env, n) {
  const limit = Math.max(1, Math.min(20, parseInt(n, 10) || 5));
  const rows = (await env.DB.prepare(
    "SELECT at, text FROM feedback WHERE accepted = 1 ORDER BY id DESC LIMIT ?"
  ).bind(limit).all()).results || [];
  return { ok: true, items: rows.map((r) => ({ at: r.at.replace("T", " ").slice(0, 16) + " UTC", text: r.text })) };
}

/* ------------------------------------------------- the file in the repository */
const GH = {
  "User-Agent": "netune-stats",
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
};

function b64encode(text) {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

function b64decode(b64) {
  const bin = atob(b64.replace(/\n/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}

async function flush(env) {
  const pending = (await env.DB.prepare(
    "SELECT id, at, text FROM feedback WHERE accepted = 1 AND committed = 0 ORDER BY id"
  ).all()).results || [];
  if (!pending.length) return true;

  const lines = pending.map((r) => r.at.replace("T", " ").slice(0, 16) + " UTC | " + r.text);
  const headers = Object.assign({ Authorization: "Bearer " + env.GITHUB_TOKEN, "Content-Type": "application/json" }, GH);
  const api = "https://api.github.com/repos/" + REPO + "/contents/" + FILE;

  // read-append-write, retried, because two people can write at once and
  // GitHub refuses the second with a stale sha rather than losing a line
  for (let attempt = 0; attempt < 4; attempt++) {
    let sha = null;
    let existing = "";
    const got = await fetch(api + "?ref=main", { headers });
    if (got.status === 200) {
      const data = await got.json();
      sha = data.sha;
      existing = b64decode(data.content || "");
    } else if (got.status !== 404) {
      return false;
    }
    if (!existing) existing = FILE_HEADER;
    if (!existing.endsWith("\n")) existing += "\n";
    const content = existing + lines.join("\n") + "\n";
    const first = pending[0].text;
    const message = "Feedback: " + (first.length > 48 ? first.slice(0, 48) + "…" : first) +
      (pending.length > 1 ? " (+" + (pending.length - 1) + " more)" : "");
    const put = await fetch(api, {
      method: "PUT",
      headers,
      body: JSON.stringify(Object.assign({ message, content: b64encode(content), branch: "main" }, sha ? { sha } : {})),
    });
    if (put.status === 200 || put.status === 201) {
      const ids = pending.map((r) => r.id);
      await env.DB.prepare("UPDATE feedback SET committed = 1 WHERE id IN (" + ids.map(() => "?").join(",") + ")")
        .bind(...ids).run();
      return true;
    }
    if (put.status !== 409 && put.status !== 422) return false;
  }
  return false;
}
