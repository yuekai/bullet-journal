---
title: DSH on legionp
description: The DeepSeek Harness web UI on legionp, its permanent tailnet bookmark, the Windows supervisor, and updates
date: 2026-10-30
---

The DeepSeek Harness (DSH) web UI runs on legionp, the Windows laptop. The
permanent bookmark is `http://legionp.taildd337d.ts.net:3081/`. The bookmark
holds no token and also works on legionp itself. The code is in
`C:\Users\yuekai\dsh-web`, a local git repo. It copies the layout of
[DSH on spark](dsh-on-spark.md), with Windows parts in place of systemd.
`README.md` in the repo holds the same detail.

This note describes the setup on 2026-10-30. It replaced the first legionp
setup from 2026-10-29: a batch supervisor that started at logon from the
Startup folder, ran `npx @deepseek-ai/dsh@0.2.1-rc.3` on `localhost:3080`, and
needed the token from its log for each new browser. That setup, its
`%LOCALAPPDATA%\dsh-web` folder, and its scripts and `DSH-WEB-SETUP.md` in the
OneDrive default workspace are deleted.

## Layout

| Port | Served by | Function |
|---|---|---|
| 3080 | `dshweb.py dsh` | `dsh web` on loopback. The token changes at each start. |
| 3081 | `tailscaled` | The static page in `C:\Users\yuekai\dsh-web\public\`. |

- `dshweb.py dsh` is the supervisor. It starts DSH, reads its startup line, and
  writes the address, with the tailnet name in place of `127.0.0.1`, to
  `public\dsh-url.txt`. It removes the file when DSH exits and starts DSH
  again 5 seconds later.
- `public\index.html` is spark's page: it fetches `dsh-url.txt` without the
  browser cache and opens that address. DSH then sets its session cookie and
  moves to its clean root. While DSH starts again, the page retries every 2
  seconds.
- Opened from disk, `index.html` hands over to the served bookmark. It cannot
  open DSH directly: DSH's cookie is `SameSite=Strict`, and a navigation that
  starts on a `file://` page is cross-site, so the browser keeps the new cookie
  off the token redirect and DSH answers 401. From the served page, port 3081
  to port 3080 is same-site.
- legionp reaches its own tailnet name through its own `tailscaled`, so the
  bookmark works on legionp too.

The `connection` row in `~\.dsh\profiles\web\cordis.patch.yml` sets
`cookieMaxAgeDays: 90` and restates
`trustedHosts: !!js ctx.webStartup.trustedHosts`, as on spark. That expression
carries the `--trusted-host legionp.taildd337d.ts.net` option of `dshweb.py`.
The rest of that patch was copied from the desktop profile on 2026-10-29 and
is now edited by hand.

These results are correct:

- Port 3080 returns 401 without a cookie. Its `/api` paths return 404 for the
  tailnet host and 403 for a host that is not trusted.
- Port 3081 returns 200 and the page.
- `:3081/dsh-url.txt` returns 200 with the address, or 404 while DSH starts
  again.
- The address returns 303 with a cookie of `Max-Age=7776000`.

## Windows parts

- Python comes from a pixi project in the repo (`pixi.toml`, `pixi.lock`,
  Python 3.13). The tasks run its `pythonw.exe`, which has no console window,
  and each child gets `CREATE_NO_WINDOW`.
- Scheduled task `\DSH\DSH Web` starts the supervisor at logon. It runs only
  while yuekai is logged on, also on battery. Task Scheduler puts it in the
  desktop session, so `dshweb start` over ssh does not tie it to the ssh
  session.
- The supervisor owns the named pipe `\\.\pipe\dsh-web-supervisor`. Only one
  process can own the name, and Windows frees it when the process dies, so a
  second supervisor exits and a stale pid cannot block a start. The pipe takes
  `status`, `stop`, and `hold`. A hold stops DSH and keeps it stopped while the
  holder keeps its connection open.
- DSH runs on the pixi global Node (`~\.pixi\envs\nodejs\node.exe`) from the
  private npm prefix `dsh-web\npm`, so a `pixi global` reinstall of `nodejs`
  cannot remove it.
- `tailscaled` on legionp is the Windows service and is not in unattended mode,
  so the tailnet and DSH are both down while nobody is logged on.

## Tailnet

```bat
tailscale serve --bg --tcp=3080 tcp://127.0.0.1:3080
tailscale serve --bg --http=3081 C:\Users\yuekai\dsh-web\public
```

`windows\setup.ps1` in the repo sets both rules and registers the two tasks;
`-Uninstall` removes them. The forward names `127.0.0.1` because `localhost`
can resolve to `::1`. There is no Tailscale Service and no tag. The member
grant covers both ports. See [tailnet-config.md](tailnet-config.md).

## Operations

```bat
C:\Users\yuekai\dsh-web\dshweb.cmd status    :: supervisor, versions, probes, serve rules, tasks
C:\Users\yuekai\dsh-web\dshweb.cmd restart   :: new DSH token; the bookmark stays correct
C:\Users\yuekai\dsh-web\dshweb.cmd stop
C:\Users\yuekai\dsh-web\dshweb.cmd start
```

A restart retires the DSH token. A cookie already issued stays valid until it
expires. To end every cookie at once, delete the
`client-connection/browser-session` record from `~\.dsh\.credentials.yaml`
and restart.

Logs are in `dsh-web\logs`: `dsh.log` (the supervisor and DSH output; the
startup line holds the token), `update.log`, and `crash.log` for tracebacks,
since `pythonw` has nowhere to print them. Each rolls over to `<name>.1` past
5 MB.

On spark, DSH disables its Settings page on a non-localhost host. The page
opened from disk cannot reach `127.0.0.1` with the cookie (see above), so for
the full Settings page on legionp, paste the `dsh-url.txt` address into the
address bar with the host changed to `127.0.0.1`. A typed address is
same-site, so the cookie survives the token redirect; a fresh Edge profile
reached DSH this way.

## Updates

Scheduled task `\DSH\DSH Web update` runs `dshweb.py update` at 02:30 Pacific,
which is 05:30 Eastern like spark. A missed run happens when legionp is next
available. It follows npm's `next` tag, as on spark, with one Windows step:
Windows locks files in use, so the updater holds the supervisor (DSH stops),
installs, then releases the hold. It waits 90 seconds for a new address and an
HTTP answer, and reinstalls the previous version if either fails. An updater
that dies mid-install drops its pipe connection, which releases the hold.

The install needs the same `--allow-scripts` list as spark. On Windows the
`node-pty` and `koffi` prebuilds install without a build.

The desktop app shares `~\.dsh` and updates on its own schedule. On
2026-10-30 it ran 0.2.1-rc.3 while DSH Web ran 0.2.1-rc.5. A newer build can
write files the older app cannot read, so `dsh-web\backup\20261030T000700`
holds `~\.dsh\storages` and the web patch from before the first rc.5 start.

## History

- 2026-10-29: DSH Web started on legionp on `localhost:3080` through `npx`,
  pinned to 0.2.1-rc.3 to match the desktop app, with a 30-day cookie.
- 2026-10-30: `C:\Users\yuekai\dsh-web` replaced that setup. The bookmark
  became `http://legionp.taildd337d.ts.net:3081/`, the cookie lifetime 90 days,
  and the version npm's `next` (0.2.1-rc.5). The repo commits are `1631e93`,
  `56a4997` and `00dd2f3`.
