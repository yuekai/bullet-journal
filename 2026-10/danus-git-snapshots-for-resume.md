---
title: Git snapshots for Danus resume
description: How to use nested git repos inside Danus/runtime/ to snapshot a project (workers, global memory, fact graph) and resume from a commit
date: 2026-10-30
---

Question: [Danus](https://github.com/umich-fatml/danus) creates worker dirs under `runtime/`, and the top-level `Danus/` is already a git repo. How should git-based resume (commit worker dirs, resume from commits) be set up without a mess of nested repos? Layout facts come from the README and `CLAUDE.md` of [frenzymath/Danus](https://github.com/frenzymath/Danus); the storage code was not read.

## Conclusions

- **Nesting is fine if the outer repo ignores the inner path.** Put `/runtime/` in `Danus/.gitignore`. Otherwise `git add` records an embedded repo as a gitlink and warns. Submodules and subtrees are the wrong tools: they pin or copy other people's repos, and these repos are generated state.
- **One repo per project, not per worker.** A resume point is only useful if workers, `global_memory/` and `fact_graph/` all come from the same moment. Per-worker repos would snapshot only private state and make the shared artifacts unrecoverable. All of it lives under `runtime/projects/<p>/`, so that directory is the work tree, with workers as plain subdirectories.
- **Keep the git metadata outside the work tree.** `git init --separate-git-dir=runtime/.gitstore/<p>.git runtime/projects/<p>`. Agents running `git` inside a worker dir then find nothing, and cannot delete or rewrite the history.
- **A snapshot must be a consistent cut.** `git add -A` over a tree that is being written can capture a fact without the dependency it cites (the dependency's directory was scanned before it was written). Danus's MCP gateway is the only writer to the truth stores, so add a snapshot lock there: block `fact_submit`, `gm_add` and `fact_revoke`, commit, release. A copy-on-write filesystem snapshot (reflink, btrfs, zfs, LVM) committed from the copy also works; a plain `cp` does not.
- **Mutable single-file stores need care.** SQLite, if used, should go in via `.backup` or a WAL checkpoint under the lock. Append-only or one-file-per-fact stores are fine under the lock.
- **Checkpoint at round boundaries.** Commit after each worker round or `fact_submit`, not mid-round. Tag snapshots (`snap-N`) and put the round number and fact count in the commit message.

## Resume

- **Full resume (the main case):** `danus stop <p>`, `git reset --hard snap-N && git clean -fd` with the `--git-dir`/`--work-tree` flags, restart the services, `danus start <p>`. The verifier is stateless, so nothing to restore. Because the cut is consistent, restored worker notes cannot cite facts missing from the restored graph.
- **One worker only:** `git checkout snap-N -- workers/<w>` restores just that worker and leaves the shared stores current. Then check its cited fact IDs against the graph (cascade revocation may have removed some) and re-inject the current `master_guidance`.

## Open questions

- Storage format of `fact_graph/` and `global_memory/` (files, JSONL, SQLite) and whether writes are atomic.
- Where each worker's codex session state lives. If outside the project dir, snapshots miss it; either point each worker's codex home inside `workers/<w>/` or treat resume as a fresh session started from restored notes and graph.
- Whether anything in a worker dir refers to shared stores by absolute path or symlink.
- Keep secrets out of snapshot history: `config/*.env` is outside `runtime/projects/`, but workers must not write tokens into their own dirs.
