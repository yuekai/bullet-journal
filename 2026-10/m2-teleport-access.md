---
title: Reaching m2 from spark and legionp
description: How the MBZUAI m2/m1 Teleport credentials reach the remote hosts, and how to use them
date: 2026-10-31
---

m2 and m1 are MBZUAI HPC login nodes behind Teleport (`mbzuai-hpc.teleport.sh`),
authenticated with Okta SSO and biometrics. That sign-in needs a browser and the user's
phone, so it happens on the Mac and nowhere else. Every other machine works from a copy
of the Mac's `~/.tsh`, which is a bearer credential with a 24-hour TTL.

## Refreshing

On the Mac: `tsh logout; tsh login --proxy=mbzuai-hpc.teleport.sh:443`. The logout
matters: a login made while the old session is still valid does not extend it.

The Mac's `tsh` is a wrapper. After a successful login it runs `copy-tsh-credentials`,
which copies `~/.tsh` to **spark** and **legionp**, then verifies each copy by comparing
the sha256 of the certificate and private key with the Mac's. Nothing needs to be run on
either remote host.

If a copy failed (the Mac was offline at login time, say), run `copy-tsh-credentials` on
the Mac to retry. `copy-tsh-credentials --list` shows the destinations and
`copy-tsh-credentials --status` shows, per destination, when it last copied and whether
its certificate still matches the Mac's. The log is `~/Library/Logs/tsh-credentials.log`.

## Using it

- **spark**: `ssh m2` works directly. `~/.ssh/config` has `Host m2` →
  `m2-login-001.mbzuai-hpc.teleport.sh`, and the tsh-generated block beside it supplies
  the certificate paths and `ProxyCommand tsh proxy ssh`. `tsh` is `~/.local/bin/tsh`.
- **legionp**: the same block with Windows paths plus `m2` and `m1` aliases; `tsh.exe`
  sits in `%USERPROFILE%\.local\bin` and is on the user PATH.

Connections through the tunnel take 10-20 seconds and occasionally hang, so retry once or
twice before suspecting anything else. Keep long work detached (`sbatch`, or `tmux`/
`nohup` on the login node) so a dropped session does not kill it.

## Failure modes

- `certificate has expired`, `ssh: cert is not yet valid`, `Permission denied
  (publickey)`, or a sudden attempt to open a browser: the copy on that host is stale.
  Log in again on the Mac; do not retry in a loop.
- Never run `tsh login` or `tsh logout` on a remote host: login needs a browser, and
  logout deletes the copied credentials.
- Do not edit, move or copy anything under `~/.tsh`, and never print key material. A copy
  never deletes anything and always excludes `~/.tsh/bin`, so a host's own tsh files
  survive.