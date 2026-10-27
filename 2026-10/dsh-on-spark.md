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
