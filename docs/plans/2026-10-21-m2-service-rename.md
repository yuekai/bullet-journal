# Rename the llama tailnet service to m2 and drop the Kimi UI

Status: done (2026-10-21).

## Goal

The llama stack on m2 advertised the Tailscale service `svc:llama`
(`llama.taildd337d.ts.net`). The machine is `m2`, and the stack now serves
several models, so the name no longer described it. The owner asked for four
changes in one deployment:

1. Rename the tailnet service from `llama` to `m2`.
2. Remove the Kimi Code web UI from the service job; the owner uses DSH only.
3. Check the DSH proxy: it sometimes needed one page refresh to pick up a new
   DSH auth token. The owner suspected the spark setup had solved this.
4. Auto-update DSH daily as part of the service job, as on spark.

## Steps

1. Tailnet: define `svc:m2` through the API, update the policy (member grant,
   policy test, `autoApprovers.services`), then requeue the service job, then
   delete `svc:llama`. This order means the new advertisement is
   auto-approved and the old name never points at a dead backend for long.
2. Config: drop `kimi_port`; add a `[update]` section (`time`, `timezone`,
   `tag`, `health_timeout`); derive the service name from `public_host`; set
   `public_host = "m2.taildd337d.ts.net"`.
3. Service: remove the `kimi` component factory; register a `dsh-update`
   control loop; change the tailnet component to advertise the derived name
   on three ports.
4. New module `llama/dshupdate.py`: daily npm-tag check, install, restart only
   the `dsh` child, health check with rollback, catch-up, force file, one log
   line per run.
5. Tests: `tests/test_update.py` for the config, the schedule, and the four
   run paths; rerun the suite (54 tests).
6. Docs: update `README.md`, `docs/tailnet-config.md`, `docs/dsh-web-ui.md`,
   `docs/kimi-code-web-ui.md`.
7. Clients: change the `llama` provider base URL in the mbp profiles and the
   spark web profile.

## Findings on the refresh complaint

The DSH auth model, verified in the DSH client connection code: the
`?token=` URL only mints a 30-day signed cookie, and the page then
authenticates by cookie alone. The gate in front of DSH holds a fixed token
and redirects to the DSH launch URL; while DSH restarts it answers 503 for a
few seconds. So a refresh is only needed in a restart window, and the daily
update plus the crash relaunch are the only routine windows. Keeping the
gate identical to spark's was the chosen fix, plus documentation; an
auto-retrying 503 page was rejected as extra machinery.

## Verification

- `pixi run llama validate` and `pixi run test` pass on m2.
- `pixi run llama status` shows gateway, dsh, gate, and tailnet components,
  both glm-main engines adopted, and the update loop healthy.
- From mbp: port 8000 `/health` 200, 3080 401, 3081 302, 58627 refused; DNS
  `m2.taildd337d.ts.net` resolves to the new VIPs.
- The gate token URL redirects to the live DSH launch URL.
- The force file ran one update: "up to date at 0.2.1-rc.2".
- `dsh --dump-config` shows the new base URL in the web and headless mbp
  profiles and the spark web profile; the desktop profile is
  Electron-managed and reads the same file.
