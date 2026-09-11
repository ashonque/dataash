-- netune-stats: what the Worker keeps. Applied by worker/deploy.py; safe to
-- run again, because every statement creates only what is missing.

-- +1 per event per day; the totals are sums over this
CREATE TABLE IF NOT EXISTS counts (
  event TEXT    NOT NULL,
  day   TEXT    NOT NULL,           -- YYYY-MM-DD, UTC
  n     INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (event, day)
);

-- every accepted piece of feedback, and whether it has reached the repository
CREATE TABLE IF NOT EXISTS feedback (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  at        TEXT    NOT NULL,       -- ISO 8601, UTC
  text      TEXT    NOT NULL,
  page      TEXT,
  accepted  INTEGER NOT NULL DEFAULT 1,
  committed INTEGER NOT NULL DEFAULT 0
);

-- the rate limit: a hash of address and day, and when it last wrote.
-- Rows older than a day are deleted on every submission.
CREATE TABLE IF NOT EXISTS limits (
  key TEXT    PRIMARY KEY,
  at  INTEGER NOT NULL             -- unix seconds
);
