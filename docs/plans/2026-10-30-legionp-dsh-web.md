# Replace legionp's DSH Web setup with a spark-style bookmark page

Status: done (2026-10-30).

## Goal

legionp ran DSH Web from a batch supervisor on `localhost:3080`, pinned to
0.2.1-rc.3, and every new browser needed the token from its log. The owner
asked for spark's setup on legionp:

1. The bookmark is `http://legionp.taildd337d.ts.net:3081/`, with DSH on 3080.
2. No need to keep the old serving stack; remove it all.
3. Follow npm's `next` tag daily, as spark does, even though the desktop app
   on legionp stays on rc.3.
4. Python through a pixi project rather than Node: it mirrors spark's
   `dshweb.py`, and `pythonw.exe` needs no hidden-window wrapper.
5. The DSH cookie lasts 90 days.

## Design

- `C:\Users\yuekai\dsh-web` is a local git repo: `dshweb.py`, `dshweb.cmd`,
  `pixi.toml`, `public\index.html`, `windows\setup.ps1`, `README.md`.
- Scheduled tasks replace systemd: `\DSH\DSH Web` at logon runs the
  supervisor; `\DSH\DSH Web update` runs daily at 02:30 Pacific. Both run
  `pythonw.exe`, only while logged on, and also on battery.
- The supervisor restarts DSH itself and owns a named pipe instead of a lock
  file. The pipe also carries `stop`, `status`, and `hold`; the updater holds
  DSH stopped while npm replaces its files, which Windows would otherwise lock.
- DSH installs under a private npm prefix in the repo and runs on the pixi
  global Node directly.
- `tailscaled` forwards tcp:3080 to `127.0.0.1:3080` and serves `public\` on
  http:3081. The live tailnet policy does not change.

## Deviation

The plan first had the page, opened from disk, open DSH on `127.0.0.1` through
a token script. Edge showed that this lands on a 401: DSH's cookie is
`SameSite=Strict`, and a navigation that starts on a `file://` page is
cross-site, so the cookie is withheld on the token redirect. legionp can reach
its own tailnet name, so the page now uses spark's `dsh-url.txt` fetch, and
from disk it hands over to the served bookmark.

## Outcome

Every check passed:

- **From the Mac.** `:3081/` returns 200, `dsh-url.txt` holds the tailnet
  address, and `:3080/` returns 401 without a cookie. The token gives 303 with
  `Max-Age=7776000`. `/api` returns 404 for the tailnet host and 403 for a
  foreign one. A fresh headless Chrome profile landed on DSH.
- **On legionp.** Headless Edge opened the page from disk and landed on DSH
  through the bookmark.
- **Restarts and the updater.** A restart kept the old cookie valid. Killing
  DSH brought it back in 7.6 s, and a hold stopped DSH until it was released.
  A second update reported up to date at 0.2.1-rc.5.
- **Old setup.** The old Startup entry, runtime folder and OneDrive scripts
  are deleted. `DSH-MIRROR.md` now points at the new repo.

The repo commits are `1631e93`, `56a4997` and `00dd2f3`. See
[dsh-on-legionp.md](../../2026-10/dsh-on-legionp.md).
