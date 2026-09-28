#!/usr/bin/env bash
# Enable this repo's git hooks and link the bullet-journaling skill into each
# harness's user-level skills directory. Safe to rerun.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
skill="$repo/skills/bullet-journaling"

git -C "$repo" config core.hooksPath .githooks
echo "git hooks: $repo/.githooks"

# ~/.agents/skills is read by both Codex and DeepSeek Harness (DSH).
for dir in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.kimi-code/skills"; do
  target="$dir/bullet-journaling"
  mkdir -p "$dir"
  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "skip: $target exists and is not a symlink; remove it and rerun" >&2
    continue
  fi
  ln -sfn "$skill" "$target"
  echo "linked: $target -> $skill"
done
