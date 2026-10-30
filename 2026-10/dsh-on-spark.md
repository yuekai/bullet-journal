---
title: DSH on spark
description: The DeepSeek Harness web UI on spark, its permanent tailnet bookmark, providers, and operations
date: 2026-10-18
---

The DeepSeek Harness (DSH) web UI runs on spark. The permanent bookmark is
`http://spark.taildd337d.ts.net:3081/`. The bookmark holds no token. The code
is in `~/dsh-web` on spark. This instance is separate from the DSH instance in
the llama stack on m2. See [llama-serving-stack.md](llama-serving-stack.md).

This note describes the setup on 2026-10-30. `~/dsh-web/README.md` on spark
holds the same detail.

## Layout

One systemd user unit runs DSH, and spark's `tailscaled` serves a static page.
Linger is on, so the unit runs without a login.

| Port | Served by | Function |
|---|---|---|
| 3080 | `dsh-web` unit | `dsh web` on loopback. The token changes at each start. |
| 3081 | `tailscaled` | The static page in `~/dsh-web/public/`. |

- Both units run `dshweb.py` under the repo's own pixi Python
  (`~/dsh-web/pixi.toml`, python 3.13, `.pixi/envs/default/bin/python`), not
  Ubuntu's `/usr/bin/python3`. Run `pixi install` there after a fresh clone.
- `dshweb.py dsh` starts DSH. The script reads DSH's startup line and writes
  the current address to `public/dsh-url.txt`. The script removes the file
  when DSH exits.
- `public/index.html` fetches `dsh-url.txt` without the browser cache and
  opens that address. DSH then sets its session cookie and moves to its clean
  root. While DSH starts again, the file is missing, so the page says so and
  tries again every 2 seconds.
- The page holds no token, so a cached copy is harmless. The static server
  ignores the query string, so an old `:3081/?token=…` bookmark still reaches
  the page.
- Only `index.html` and `dsh-url.txt` are in `public/`. `tailscaled` serves
  each file in the folder.

The DSH session cookie lasts 90 days. DSH's default is 30. Each visit to the
bookmark makes a new cookie. The `connection` row in
`~/.dsh/profiles/web/cordis.patch.yml` sets `cookieMaxAgeDays: 90`. A patch
replaces the whole config of a row, so the row also restates
`trustedHosts: !!js ctx.webStartup.trustedHosts`. That expression carries the
`--trusted-host spark.taildd337d.ts.net` option of `dshweb.py`. Without it,
DSH refuses API requests that name the tailnet host. Check the composed row
after a DSH update with `dsh --profile web --dump-config`.

These results are correct:

- Port 3080 returns 401 without a cookie. Its `/api` paths return 403 for a
  host that is not trusted.
- Port 3081 returns 200 and the page, with or without a query string.
- `:3081/dsh-url.txt` returns 200 with the address, or 404 while DSH starts
  again.
- The address returns 303 with a cookie of `Max-Age=7776000`.

Anyone who can reach port 3081 can read the current DSH token. Only tailnet
members can reach spark, and the tailnet has one user.

## Tailnet

There is no Tailscale Service and no tag. spark's own system `tailscaled`
serves the two ports. The daemon runs as root with a persistent state file,
so the rules survive a restart. `OperatorUser=yuekai` permits
`tailscale serve` without sudo.

```bash
tailscale serve --bg --tcp=3080 tcp://127.0.0.1:3080
tailscale serve --bg --http=3081 /home/yuekai/dsh-web/public
```

The rule on port 3081 is HTTP, not HTTPS. HTTPS certificates are off for the
tailnet, and DSH itself is HTTP on port 3080. Other spark services can use
other ports.

On 2026-10-18 the machine changed from `dgx-spark` to `spark`. Key expiry is
disabled, so the node keeps its identity. The member grant covers the two
ports. A policy test pins `100.91.181.87:3080` and `100.91.181.87:3081`. See
[tailnet-config.md](tailnet-config.md).

## Providers

The DSH home is `~/.dsh`. Each profile owns its model catalog in its own
`~/.dsh/profiles/<profile>/cordis.patch.yml`: the `web` and `headless` patches
each carry an `llm-pi-ai` and an `agent-default-model` row. The home patch
`~/.dsh/cordis.patch.yml` holds only the machine-wide MCP servers; a model row
there is applied after the profile layer, shadows it, and makes the web
Settings -> Models page refuse to save. The two profile copies are independent,
so edit both when a model change should apply to both.

- The `m2` provider uses `openai-completions` at
  `http://m2.taildd337d.ts.net:8000/v1` with `LLAMA_API_KEY`. The model list
  holds `deepseek-v4.1-flash`, `kimi-k3`, and `glm-5.3`. New sessions in every
  profile use `deepseek-v4.1-flash` with high effort. The host changed from
  `llama.taildd337d.ts.net` on 2026-10-21, when the stack renamed its service
  to `svc:m2`; the service was restarted to pick up the new patch.
- The `anthropic` route lists three Claude models and resolves
  `ANTHROPIC_API_KEY` from the credential store, which the web profile mounts;
  the headless profile disables that store, so a headless session needs the key
  in its environment.
- The built-in DeepSeek API provider uses `DEEPSEEK_API_KEY`. The same key
  enables web search.

`~/dsh-web/.env` holds the two keys with mode 600, and the unit loads it
through `EnvironmentFile`. A `dsh headless` run started from a shell has no
keys unless `~/.env` is sourced first, so it cannot reach `m2` until then. The
keys came from m2 `~/llama/api-key.yaml` and m2 `~/.env`.

The `m2` provider depends on the llama stack. When the stack is down, use the
DeepSeek API provider.

DSH disables its Settings page on a non-localhost host. Use `/model` or the
model control in a session. For the full Settings page, run
`ssh -N -L 127.0.0.1:3080:127.0.0.1:3080 spark`. Then open the native address
with the host name `127.0.0.1`.

## Install

DSH follows npm's `next` tag (release candidates), not `latest` or `alpha`
(see [Updates](#updates)). On 2026-10-18 that was 0.2.1-rc.2, the same as m2.
npm installs DSH under the private prefix `~/dsh-web/npm/` (not in git), so
the binary is `~/dsh-web/npm/bin/dsh`. legionp uses the same layout. Node is
the `pixi global` env `nodejs`, pinned to `24.*`. `~/.pixi/envs/nodejs/bin`
comes first on the units' PATH.

Important: the npm install needs `--allow-scripts` for
`@deepseek-ai/dsh-subprocess-local`, `koffi`, `node-pty`, `@google/genai`, and
`protobufjs`. Without this option, npm skips the native steps that the
terminal and bash tools need. The arm64 native packages
(`node-addon-system-linux-arm64`, `node-pty` prebuilds) install without a
build.

A `pixi global` reinstall of `nodejs` no longer removes DSH. Native modules
are built for one Node ABI, though. After the env changes major version, run
`npm install -g --prefix ~/dsh-web/npm --allow-scripts=<the list above> @deepseek-ai/dsh@next`
again.

## Operations

```bash
systemctl --user status dsh-web
systemctl --user restart dsh-web       # new DSH token; the bookmark stays correct
cat ~/dsh-web/public/dsh-url.txt       # the current DSH address
tailscale serve status                 # tcp:3080 and http:3081
```

A restart retires the DSH token. A cookie that DSH already issued stays valid
until it expires, up to 90 days. To end every cookie at once, delete the
`client-connection/browser-session` record from `~/.dsh/.credentials.yaml`.
That record holds the cookie signing key. Then restart `dsh-web`.

`~/dsh-web/logs/dsh.log` holds the DSH output with mode 600. The startup line
holds the DSH token. Each log in `logs/` rolls over to `<name>.1` past 5 MB.
The user journal on spark is unreadable, so the logs are files.

## Updates

`dsh-update.timer` runs `dshweb.py update` at 05:30 America/New_York each day.
A missed run happens at the next boot.

- If the installed version differs from npm's `next` tag, the script installs
  `next` and restarts `dsh-web`.
- The update counts as good when DSH publishes a new address and port 3080
  answers within 90 seconds.
- If the install or the check fails, the script installs the previous version
  again and exits nonzero.
- Each run adds one line to `~/dsh-web/logs/update.log`.

```bash
systemctl --user list-timers dsh-update.timer   # next run
systemctl --user start dsh-update               # run it now
```

A manual install of another version lasts only until the next run.

## History

- 2026-10-18: The spark Kimi Code web UI was removed. The steps were the
  `kimi-web` unit, its process, and the serve entry on port 58627. Its
  install directory was already gone, so the process could not start again.
  `~/.kimi-code` stays.
- 2026-10-18: DSH started on spark at `spark.taildd337d.ts.net:3081`.
- 2026-10-18: The daily update timer and the log cap were added. The first
  run moved DSH from 0.2.1-rc.2 (`next`) to 0.2.0-rc.2 (`latest`).
- 2026-10-18: The update switched from the `latest` tag to the `next` tag,
  which moved DSH back to 0.2.1-rc.2.
- 2026-10-26: The model catalog moved out of the home patch into the `web` and
  `headless` profile patches, so the Settings -> Models page can edit each
  profile again. The home patch keeps only the MCP servers.
- 2026-10-29: A static page served by `tailscaled` on http:3081 replaced the
  fixed-token gate. The `dsh-gate` unit, `~/.dsh/web.token`, and
  `state/dsh-gate-url.txt` were removed. The bookmark became
  `http://spark.taildd337d.ts.net:3081/` with no token. The DSH cookie
  lifetime went from 30 days to 90 days. A verification run of the update
  moved DSH from 0.2.1-rc.4 to 0.2.1-rc.5.
- 2026-10-30: Matching legionp, the units moved to a pixi Python in
  `~/dsh-web` and DSH moved to the private prefix `~/dsh-web/npm/`. The pixi
  `nodejs` env was pinned to `24.*`, which moved it from 26.10.0 to 24.22.1.
  DSH stayed at 0.2.1-rc.5.
