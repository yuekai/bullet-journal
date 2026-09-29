#!/usr/bin/env bash
# Enable this repo's git hooks and link each skill in skills/ into each
# harness's user-level skills directory. Safe to rerun.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
retired=(bullet-journaling)  # old skill names whose links should be removed

git -C "$repo" config core.hooksPath .githooks
echo "git hooks: $repo/.githooks"

# ~/.agents/skills is read by both Codex and DeepSeek Harness (DSH).
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.kimi-code/skills"; do
  mkdir -p "$dir"
  for name in "${retired[@]}"; do
    old="$dir/$name"
    if [[ -L "$old" && "$(readlink "$old")" == "$repo/skills/"* ]]; then
      rm "$old"
      echo "removed: $old"
    fi
  done
  for skill in "$repo"/skills/*/; do
    skill="${skill%/}"
    target="$dir/$(basename "$skill")"
    if [[ -e "$target" && ! -L "$target" ]]; then
      echo "skip: $target exists and is not a symlink; remove it and rerun" >&2
      continue
    fi
    ln -sfn "$skill" "$target"
    echo "linked: $target -> $skill"
  done
done
