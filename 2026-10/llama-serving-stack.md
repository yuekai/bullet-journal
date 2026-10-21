---
title: Llama serving stack
description: The llama cluster service on m2 — model engines, gateway, the DSH web UI, and the tailnet endpoint
date: 2026-10-18
---

The llama stack serves two models on the m2 Slurm cluster. The models are
`deepseek-v4.1-flash` and `kimi-k3`. The stack runs from `~/llama` on m2. The
stack serves an OpenAI-compatible API on the tailnet. The stack also hosts the
DSH web UI and keeps that UI current with a daily update.

One service job runs the gateway, the web UI, and the control loops. Each
model replica runs in a separate GPU allocation. The allocation can span two
nodes.

This note describes the stack on 2026-10-21. The documents in `~/llama/docs`
hold the mechanism detail.

## Layout

One CPU allocation owns all of these parts:

- The SMG gateway. SMG supplies the HTTP routing, the authentication, and the
  stream support.
- The DSH web UI.
- The DSH redirect gate.
- The userspace Tailscale client.
- The worker registration loop.
- The replica counter.
- The daily DSH update loop.

The engine jobs serve the models. A pool holds a group of engine jobs for one
recipe. `llama.toml` gives the pools and the replica targets. This table gives
the standard targets:

| Pool | Recipe | Partition | Replicas | Nodes for each job | GPUs for each job |
|---|---|---|---|---|---|
| `kimi-main` | `kimi-k3` | `main` | 1 | 2 | 16 |
| `kimi-lowprio` | `kimi-k3` | `lowprio` | 2 | 2 | 16 |
| `deepseek-main` | `deepseek-v4.1-flash` | `main` | 1 | 1 | 8 |

The full stack needs 56 GPUs. Each node supplies 8 GPUs, 96 CPUs, and
1152 GiB of memory.

The controller reads `llama.toml` again every 60 seconds. The controller
validates the file and each recipe. A bad file changes nothing; the controller
keeps the current fleet.

## Endpoints

The Tailscale service `svc:m2` gives the three endpoints. The tailnet name is
`m2.taildd337d.ts.net`. A tailnet move or a service restart does not change
these names.

| Port | Function | Authentication |
|---|---|---|
| 8000 | SMG gateway, `/v1` | Bearer key from `api-key.yaml` |
| 3080 | DSH web UI | Rotating token, URL in `state/dsh-url.txt` |
| 3081 | DSH redirect gate | Fixed token from `~/.dsh/web.token` |

The gateway answers `/health` and `/v1/models` without a key. The gateway
needs the engine key for `/workers`. The engine key is in `engine-key.yaml`.

The member grant for `svc:m2` covers all three ports. A policy test covers
the same three ports. See [tailnet-config.md](tailnet-config.md) for the access rules.

## Model engines

Each engine job makes one launch attempt. The step is:

1. The engine writes a start record. The record holds the job ID, the Slurm
   restart count, and a launch ID.
2. The engine finds the local weights and one image digest. The engine
   prepares the container on each node.
3. The engine starts all ranks in one step. The step uses
   `--kill-on-bad-exit=1`.
4. The engine reports the model ready when `/v1/models` answers with the
   correct model name.
5. On a rank failure, the engine marks the record stopped and removes the
   step. The controller then asks for a replacement allocation.

The start deadline is two hours. The deadline includes the preparation step.
A clean exit still counts as a rank failure. This rule stops the other ranks.

Important: a job can be RUNNING while the model is not ready. The engine
imports the container and loads the weights for a long time. On 2026-09-21,
the jobs started at 18:50 UTC. Three engines became ready at 19:09 UTC, about
19 minutes later. The `kimi-main` engine became ready at about 19:50 UTC, one
hour later. Do not stop a job while the phase is `starting`.

The controller counts allocations in each state. The states are pending,
starting, suspended, and completing. The controller submits one replacement
for a pool in 300 seconds at most. The controller cancels pending jobs first
during a scale-down. The controller then cancels the newest running jobs.

Each job comment holds the workspace hash, the pool name, and a submission
ID. The controller does not touch a fleet with different marks.

## Gateway

SMG routes each request and authenticates each request. SMG also supplies the
stream support. The client retries a request or a stream after an engine
change.

Python supervises the gateway, the web UI, Tailscale, and the update loop.
Python starts a dead process group again after 10 seconds. The gateway has a
health deadline of 60 seconds at start. A gateway restart does not stop the
web UI.

The registration loop reads the worker list from SMG every 10 seconds. The
loop adds each ready worker. The loop also refreshes each entry that this
stack owns. The loop removes each entry that is no longer correct. The
registration data holds the models, the engine authentication, and the
capacity. The registration data holds no keys. A loaded engine stays alive
during a registration fault.

Use `/workers` on the gateway for the true worker list. The command is:

```bash
curl -s -H "Authorization: Bearer <engine-key>" \
  http://m2.taildd337d.ts.net:8000/workers
```

The `registry` field in `pixi run llama status` can read `null` between two
updates. Use `/workers` when the answer must be exact.

## The Kimi Code web UI (removed)

The stack ran the Kimi Code web UI as the `kimi` component until 2026-10-21.
The owner now uses DSH only. The component, port 58627, and the service
advertisement of that port are gone. The shared home `~/.kimi-code` (token,
sessions, `bin/kimi`) stays on disk, so a manual start is still possible.
The full history, including the 8 GiB V8 heap repair and the port guard, is
in `~/llama/docs/kimi-code-web-ui.md`. The `spark` copy was removed on
2026-10-18. spark now runs its own DSH web UI. See
[dsh-on-spark.md](dsh-on-spark.md).

## DSH web UI

DSH runs as the `dsh` component of the service job. DSH rotates its browser
token at each process start. `state/dsh-url.txt` holds the current address.

The `dsh-update` loop keeps the vendored DSH on npm's `next` tag, like the
timer on spark. Each day at 05:30 America/New_York it compares `vendor/dsh`
with `npm view @deepseek-ai/dsh@next version`. A difference installs the new
version, restarts only the `dsh` child, and waits up to 90 seconds for a new
launch URL and an HTTP answer on port 3080. A failed install or check puts
the old version back the same way. A missed run catches up at service start.
`touch state/dsh-update.force` runs one update now. Each run adds one line to
`logs/service/update.log` and a record to `state/dsh-update.json`. A hand
`npm install` inside `vendor/dsh` lasts only until the next run.

The gate in front of DSH holds a fixed token. The gate listens on port 3081
and answers the fixed token with a redirect to the DSH address. The file
`~/.dsh/web.token` holds the token with mode 600. `state/dsh-gate-url.txt`
holds the permanent address. A bookmark on the gate address stays correct
after a DSH restart.

Use `rm ~/.dsh/web.token` to change the fixed token. The gate makes a new
token at the next request. The file `state/dsh-gate-url.txt` changes in a few
seconds. Old addresses return 401 at once. A live DSH session continues.

The DSH session cookie belongs to the host that made it. After the 2026-10-21
rename from `llama.taildd337d.ts.net`, each browser needs one visit of the
permanent bookmark to make a cookie for `m2.taildd337d.ts.net`. While DSH
restarts (the daily update, or a crash relaunch), the gate answers 503 for a
few seconds and the page needs one reload after the new address appears. The
cookie itself survives a restart.

These results are correct:

- Port 3080 returns 401 without a token. The port is open.
- Port 3081 returns 302 and points to port 3080.

The DSH settings file is `~/.dsh/settings.yaml`. Llama supplies
`LLAMA_API_KEY` to the process. The `llama` provider uses the
`openai-completions` form at `http://127.0.0.1:8000/v1`. The model list holds
`deepseek-v4.1-flash` and `kimi-k3`.

DSH disables the browser settings page on a non-localhost host. The Models
page then reports a settings fault. Use the model control near the chat input
or the `/model` command to choose a model from the tailnet. DSH shows this
control only inside a session.

For the full settings page, forward a local port to the tailnet endpoint. Run
this command on the machine with the browser:

```bash
pixi exec --spec socat -- socat \
  TCP4-LISTEN:3080,bind=127.0.0.1,reuseaddr,fork \
  TCP:m2.taildd337d.ts.net:3080
```

Open the address from `state/dsh-url.txt`. Replace the host name with
`127.0.0.1`. Keep the port and the token. See `~/llama/docs/dsh-web-ui.md`.

## Tailnet exposure

The stack starts a userspace `tailscaled` as a supervised child. The options
are `--tun=userspace-networking` and `--state=mem:`. The machine joins the
tailnet as `llama-gateway` with the tag `tag:llama-gateway`.

The machine advertises the service `svc:m2` on ports 8000, 3080, and 3081.
The service name is the first label of `public_host` in `llama.toml`. The
`autoApprovers` rule approves the advertisement from the tag.

The stack reads `TS_AUTH_KEY` from `~/llama/.env`. The stack moves the key
through a private file and removes the file after the authentication.

A tailnet fault does not stop the cluster-side service. The gateway, the
web UI, and the engines continue to run.

`tailscale serve status` shows only the forwarding table. The command
`tailscale status --json` must also show `svc:m2` under
`Self.CapMap["service-host"]`.

## Files, state, and logs

The important paths are:

- `llama.toml` holds the pools, the service settings, and the DSH update
  schedule.
- `recipes/*.toml` hold the model launches. The recipes are
  `deepseek-v4.1-flash.toml` and `kimi-k3.toml`.
- `state/llama-gateway.json` holds `gateway_url`, the current address of the
  gateway. It also holds the job ID and the namespace.
- `state/service.json` holds the process ID, the launch ID, and the log path
  of each component.
- `state/replicas.json` holds the replica target and the job list of each
  pool.
- `state/registry.json` holds the worker entries that this stack owns.
- `state/dsh-url.txt` holds the current DSH address.
- `state/dsh-gate-url.txt` holds the permanent gate address.
- `state/dsh-update.json` holds the last update run, and
  `state/dsh-update.force` requests one now.
- `logs/slurm/` holds the Slurm output.
- `logs/service/` holds one log for each component start. The name has the
  form `<job>_<component>_<launch>.log`. `logs/service/update.log` holds the
  update runs.
- `logs/engine/` holds the engine logs, one for each rank.
- `api-key.yaml` holds the client key.
- `engine-key.yaml` holds the engine key.
- `.env` holds `TS_AUTH_KEY`.
- `vendor/tailscale/` holds the `tailscale` and `tailscaled` binaries.
- `vendor/dsh/` holds the DSH node modules.

The files `api-key.yaml`, `engine-key.yaml`, `.env`, and `vendor/` are not in
git. A new clone must make these files again.

## Operations

### Check the stack

1. Run `cd ~/llama && pixi run llama status`. This command gives the job
   state, the component state, and the replicas.
2. Run `curl -s http://m2.taildd337d.ts.net:8000/health`. The answer must
   be `OK`.
3. Run the models command with the client key:

   ```bash
   curl -s -H "Authorization: Bearer <api-key>" \
     http://m2.taildd337d.ts.net:8000/v1/models
   ```

4. Use `/workers` with the engine key for the exact worker list.
5. Send one short completion to each model. The model list alone does not
   prove that a model answers.

### Start the stack

1. Run `cd ~/llama && pixi install` after a new clone.
2. Run `pixi run llama validate`. This command checks the configuration, the
   keys, and the local model files.
3. Run `pixi run test`. The test suite has 54 tests and covers the recovery
   behaviour and the update loop.
4. Run `pixi run llama submit`.
5. Run `pixi run llama status` and wait for each engine.

The service job asks for an unlimited time by default. An engine asks for 28
days by default.

Use short times for the first start after a maintenance window. A short time
also helps when a reservation can hold the jobs:

```bash
pixi run llama submit --time 1-00:00:00 --engine-time 1-00:00:00
```

The time option applies for the life of the service, and it also applies to
each replacement. Start the stack without this option after the risk ends.

### Stop the stack

1. Set each replica target in `llama.toml` to zero.
2. Wait for each GPU job to leave Slurm.
3. Cancel the service job.

A cancel of the service job alone leaves the engines running.

### Replace one engine

1. Raise the replica target of the pool by one.
2. Wait for the new worker to report healthy in `pixi run llama status`.
3. Cancel the old job.
4. Set the replica target of the pool back to the old value.

Keep this order. A lower target cancels pending jobs and the newest running
jobs. The order above protects the new worker.

### Change a replica target

1. Edit `llama.toml`.
2. Wait 60 seconds for the controller to read the file again.

A zero stops a pool. A removed pool also stops its jobs. The service settings
in `llama.toml` need a service restart. A recipe change applies to a new
allocation only. Rename a pool to replace its allocations with a new recipe.

## Failure modes and recovery

### A cluster maintenance window holds the jobs

1. Read the reservation list with `scontrol show reservation`.
2. Confirm the reason of each job with `squeue`. The reason
   `ReqNodeNotAvail, Reserved for maintenance` means that a reservation holds
   the nodes.
3. Do nothing. Slurm reads the queue again at each cycle. The jobs start when
   the reservation ends. Do not submit the stack again.

The condition of the nodes does not matter while a reservation holds them. On
2026-09-21, all 973 GPU nodes reported zero GPUs during a driver upgrade. The
reservation `fs-cuda-13-upgrade` held the same nodes. The reservation ended at
18:49:39 UTC. All five jobs started at 18:50:32 UTC, 53 seconds later. The
models became ready at 19:09:36 UTC.

### The stack does not accept a second service job

The command `pixi run llama submit` fails when this stack already owns a
service job. Read the state with `pixi run llama status` before a new submit.
An advisory lock also blocks a second service process.

### The engine jobs report a fault after a stop

The file `state/registry.json` can hold old worker addresses after an outage.
The registration loop removes each entry that is no longer correct. Use
`/workers` for the current list. The table of the reasons is not proof of a
fault. A failed Slurm read or a failed HTTP read gives an unknown result, not
a missing job.

### An engine hangs after start

An HTTP health fault does not cancel a live GPU job. A process that hangs
after the start needs a person. Read the engine log in `logs/engine/` and
cancel the job by hand.

## Open items

- The `registry` field of `pixi run llama status` can read `null` between two
  updates.
- The file `state/registry.json` held old worker addresses after the
  2026-09-21 maintenance window.
- The `kimi-main` engine needed about one hour to become ready after the
  2026-09-21 start. The other three engines were ready in about 19 minutes.
  A long start for a large model is usual.

## Pointers

- `~/llama/README.md` holds the full description of the stack.
- `~/llama/docs/kimi-code-web-ui.md` holds the removed Kimi Code web UI
  instances and the general pattern for a Slurm cluster.
- `~/llama/docs/dsh-web-ui.md` holds the DSH web UI.
- `~/llama/docs/tailnet-config.md` holds the service and approval checks.
- [tailnet-config.md](tailnet-config.md) holds the tailnet access rules.

## History

- 2026-09-10: The llama stack replaced the m2 `kimi-serve` stack. The new
  stack used the same shared home, the same token, and the same port.
- 2026-09-14: A maintenance window stopped the first llama fleet.
- 2026-09-21: The reservation `fs-cuda-13-upgrade` held all 973 GPU nodes for
  a driver upgrade. The reservation ended at 18:49:39 UTC. The stack started
  without help at 18:50:32 UTC.
- 2026-10-21: The service name changed from `svc:llama` to `svc:m2`, so the
  tailnet name matches the machine. The Kimi Code web UI left the stack, and
  port 58627 left the service. The daily DSH update loop joined the control
  loops. The clients' provider address changed to `m2.taildd337d.ts.net`.
