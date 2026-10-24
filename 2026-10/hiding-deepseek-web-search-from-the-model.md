---
title: Hiding the DeepSeek web search from the model
description: How to remove web_search/web_fetch from a DSH session so the model must use the keenable MCP tools, and why the switch is the agent preset rather than the profile
date: 2026-10-23
---

Question asked: can the DeepSeek search be hidden from the model in DSH (Web GUI) so it is forced to rely on the keenable search MCP server? Answer: yes, but the switch sits in the agent preset, not in the profile or the Web settings. Nothing was changed; the user asked for the answer only.

## The two layers that both look like "DeepSeek search"

- **Providers, not model-visible:** `web-search-deepseek` (DeepSeek's native search run inside a Messages request) and `web-deepseek-api` (the standalone Search/Fetch API) only implement `ctx.web.search()`/`fetch()`. They cost nothing while no tool calls them and never appear in the tool catalog.
- **The actual model surface:** `web_search` and `web_fetch`, registered by `@deepseek-ai/dsh-tool-web`. Hiding "the DeepSeek search" is exactly hiding this one plugin row.

## Where the row lives (the part that matters)

- `dsh-base` mounts `tool-web` process-wide, and `dsh-web-app` disables that row for Web (`- id: tool-web` / `disabled: true` in its profile patch), because in Web every session builds its agent from an agent preset instead.
- The `standard` preset therefore carries its own `tool-web` child. Preset children are a `config.plugins` value, not loader entries, so a profile patch cannot address `id: tool-web` inside them. A patch entry assigns an entry's whole `config` key and does not deep-merge, so removing or reconfiguring that child means re-stating `preset-standard`'s complete child list under a patch keyed by the row id `preset-standard` — the documented way to override a shipped preset.
- `ptc` also mounts `tool-web`; `minimal` does not. So the override is per preset: switching mode brings the tool back.

## The two workable variants

- **Remove the row:** `web_search` and `web_fetch` both disappear, leaving `mcp__keenable__search_web_pages` and `mcp__keenable__fetch_page_content` as the only retrieval tools. Strongest form of "force keenable".
- **Keep the row with `search: false`:** `web_search` disappears but generic `web_fetch` (plain HTTP fetch of a known URL) stays available, in case reading a specific URL should not depend on the MCP server.

Both were verified by composing the web profile with a scratch `--patch` overlay and diffing `dsh --profile web --dump-config`: only the `tool-web` child (or its `search` key) changed, and the `mcp-keenable` / `mcp-keenable-webql` rows were untouched.

## Costs and gotchas

- An override replaces the complete child list, so future changes shipped to `standard` by a DSH upgrade will not merge in — the preset docs warn about this explicitly.
- Not retroactive: a running session keeps its composition for request-cache stability, so the tool catalog changes only in sessions created afterwards.
- Placement: the Web profile's own patch (`~/.dsh/profiles/web/cordis.patch.yml`). Putting it in the home layer (`~/.dsh/cordis.patch.yml`) is harmless but logs `patch: entry "preset-standard" not found` when the headless profile composes, since that profile has no presets; headless gets its tools straight from base, so there the equivalent step is disabling its `tool-web` row directly.
- Prompt-level steering (an AGENTS.md line saying "use keenable") is already what happens by default and does not hide anything — the model can still pick `web_search` when it looks convenient.

Decision: answer only, no config change, and the scratch overlays/dumps were deleted.