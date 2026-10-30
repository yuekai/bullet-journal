# Replace the spark DSH gate with a static redirect page

Status: done (2026-10-29).

## Goal

The spark DSH bookmark was `http://spark.taildd337d.ts.net:3081/?token=<fixed>`.
A Python gate held the fixed token and redirected it to DSH's current launch
URL. The fixed token was a permanent bearer secret in bookmarks and history.

The owner asked for these changes:

1. Keep a port in the URL, so other spark services can use other ports. DSH
   stays on 3080. The bookmark becomes `http://spark.taildd337d.ts.net:3081/`
   with no token.
2. spark's system `tailscaled` serves a static page on http:3081. The page
   reads DSH's current launch URL and opens it. No gate process remains.
3. Retire the gate in the same change: its unit, its serve rule, and
   `~/.dsh/web.token`.
4. The DSH browser cookie lasts 90 days instead of 30.

## Design

- `~/dsh-web/public/` is the served directory. `index.html` is static and in
  git. `dsh-url.txt` holds the launch URL while DSH runs and is gitignored.
- `tailscale serve --bg --http=3081 /home/yuekai/dsh-web/public`.
- The page fetches `dsh-url.txt` with `cache: "no-store"` and calls
  `location.replace`. While DSH restarts it retries every 2 seconds. The page
  holds no token, so a cached copy is harmless.
- HTTP, not HTTPS: the tailnet has HTTPS certificates off, and DSH itself is
  HTTP on 3080.
- Port 3081 keeps the policy test valid, and the static server ignores the
  query string, so old bookmarks still reach the page.
- The cookie lifetime is `cookieMaxAgeDays: 90` on the `connection` row of the
  spark web profile patch. A patch replaces the whole row config, so the row
  restates `trustedHosts: !!js ctx.webStartup.trustedHosts`. Without it DSH
  would stop trusting the tailnet host name.

## Steps

1. Back up and edit `~/.dsh/profiles/web/cordis.patch.yml`; check the composed
   row with `dsh --profile web --dump-config`.
2. `~/dsh-web`: `NATIVE_URL` moves to `public/dsh-url.txt`; the gate code,
   `systemd/dsh-gate.service` and the gate README sections go; add
   `public/index.html` and the `.gitignore` rule.
3. Restart `dsh-web`; disable and unlink `dsh-gate`; replace the tcp:3081
   serve rule with the http:3081 rule; delete `web.token` and the old state
   files.
4. Update `dsh-on-spark.md` and `tailnet-config.md`. The live policy does not
   change.

## Verification

- `:3081/` and `:3081/?token=x` return the page; `:3081/dsh-url.txt` returns
  the launch URL.
- The launch URL returns 303 with a cookie of `Max-Age=7776000`; the cookie
  then opens `:3080/` with the tailnet Host.
- A `dsh-web` restart makes `dsh-url.txt` return 404 and then a new token.
- `tailscale serve status` shows tcp:3080 and http:3081 only.
- `dshweb.py update` still reports a healthy install.

## Outcome

Every check passed. `/api` on 3080 returned 404 for the tailnet Host and 403
for a foreign one, so the restated `trustedHosts` works. A fresh headless
Chrome profile went from `:3081/` to DSH on `:3080/`. The update check moved
DSH from 0.2.1-rc.4 to 0.2.1-rc.5, and the `connection` row survived it. The
`~/dsh-web` commit is `5037ba0`.
