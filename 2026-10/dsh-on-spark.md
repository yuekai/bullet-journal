---
title: DSH on spark
description: The DeepSeek Harness web UI on spark, its permanent tailnet bookmark, providers, and operations
date: 2026-10-18
---

The DeepSeek Harness (DSH) web UI runs on spark. The permanent bookmark is
`http://spark.taildd337d.ts.net:3081/?token=<fixed>`. The code is in
`~/dsh-web` on spark. This instance is separate from the DSH instance in the
llama stack on m2. See [llama-serving-stack.md](llama-serving-stack.md).

This note describes the setup on 2026-10-18. `~/dsh-web/README.md` on spark
holds the same detail.

## Layout

Two systemd user units run the UI. Linger is on, so the units run without a
login.

| Unit | Port | Function |
|---|---|---|
| `dsh-web` | 3080 | `dsh web` on loopback. The token changes at each start. |
| `dsh-gate` | 3081 | Redirect gate on loopback. It holds a fixed token. |

The two processes come from one script, `~/dsh-web/dshweb.py`. The script
copies the llama design (`~/llama/llama/dshgate.py` on m2):

- `dshweb.py dsh` starts DSH. The script reads DSH's startup line and writes
  the current address to `state/dsh-url.txt`. The script removes the file
  when DSH exits.
- `dshweb.py gate` reads the fixed token from `~/.dsh/web.token`. A request
  with the fixed token gets a redirect to the current DSH address.
  `state/dsh-gate-url.txt` holds the permanent address.

These results are correct:

- Port 3080 returns 401 without a token.
- Port 3081 returns 302 to port 3080 without a token. A browser with a live
  DSH session cookie gets in this way.
- Port 3081 returns 401 for a wrong token.
- Port 3081 returns 503 for a few seconds while DSH starts again.

## Tailnet

There is no Tailscale Service and no tag. spark's own system `tailscaled`
serves the two ports with `tailscale serve --tcp=3080` and `--tcp=3081`. The
daemon runs as root with a persistent state file. `OperatorUser=yuekai`
permits `tailscale serve` without sudo.

On 2026-10-18 the machine changed from `dgx-spark` to `spark`. Key expiry is
disabled, so the node keeps its identity. The member grant covers the two
ports. A policy test pins `100.91.181.87:3080` and `100.91.181.87:3081`. See
[tailnet-config.md](tailnet-config.md).

## Providers

The DSH home is `~/.dsh`. The provider settings are in
`~/.dsh/profiles/web/cordis.patch.yml`. The file is m2's patch with one
change: the `llama` base URL.

- The `llama` provider uses `openai-completions` at
  `http://llama.taildd337d.ts.net:8000/v1` with `LLAMA_API_KEY`. The model
  list holds `deepseek-v4.1-flash`, `kimi-k3`, and `glm-5.3`. New sessions use
  `glm-5.3` with high effort.
- The built-in DeepSeek API provider uses `DEEPSEEK_API_KEY`. The same key
  enables web search.

`~/dsh-web/.env` holds both keys with mode 600. The keys came from m2
`~/llama/api-key.yaml` and m2 `~/.env`.

The llama provider depends on the llama stack. When the stack is down, use the
DeepSeek API provider.

DSH disables its Settings page on a non-localhost host. Use `/model` or the
model control in a session. For the full Settings page, run
`ssh -N -L 127.0.0.1:3080:127.0.0.1:3080 spark`. Then open the native address
with the host name `127.0.0.1`.

## Install

DSH follows npm's `latest` tag only, never `next` or `alpha` (see
[Updates](#updates)). On 2026-10-18 that was 0.2.0-rc.2. m2 runs 0.2.1-rc.2.
npm installs DSH in its default global prefix. Node comes from `pixi global install nodejs`, so the binary is
`~/.pixi/envs/nodejs/bin/dsh`.

Important: the npm install needs `--allow-scripts` for
`@deepseek-ai/dsh-subprocess-local`, `koffi`, `node-pty`, `@google/genai`, and
`protobufjs`. Without this option, npm skips the native steps that the
terminal and bash tools need. The arm64 native packages
(`node-addon-system-linux-arm64`, `node-pty` prebuilds) install without a
build.

A `pixi global` reinstall of `nodejs` removes DSH. Install DSH again after
one.

## Operations

```bash
systemctl --user status dsh-web dsh-gate
systemctl --user restart dsh-web       # new DSH token; the bookmark stays correct
cat ~/dsh-web/state/dsh-gate-url.txt   # the bookmark
rm ~/.dsh/web.token                    # new bookmark; old bookmarks return 401
```

`~/dsh-web/logs/dsh.log` holds the DSH output with mode 600. The startup line
holds the DSH token. Each log in `logs/` rolls over to `<name>.1` past 5 MB.
The user journal on spark is unreadable, so the logs are files.

## Updates

`dsh-update.timer` runs `dshweb.py update` at 05:30 America/New_York each day.
A missed run happens at the next boot.

- If the installed version differs from npm's `latest` tag, the script
  installs `latest` and restarts `dsh-web`.
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
