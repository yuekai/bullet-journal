"""Check that relative links in the repo's agent-facing docs resolve.

Covers AGENTS.md, docs/*.md and skills/**/*.md. Completed plans in docs/plans/ are
historical records, so their links to since-moved paths are left alone. Links inside
code (fenced blocks and inline spans) are examples and placeholders, not links.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*```")
CODE_SPAN_RE = re.compile(r"(`+).*?\1")


def doc_files(root: Path) -> list[Path]:
    return [root / "AGENTS.md", *sorted((root / "docs").glob("*.md")), *sorted((root / "skills").rglob("*.md"))]


def anchor(heading: str) -> str:
    """GitHub's anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(path: Path) -> set[str]:
    return {anchor(line.lstrip("#")) for line in path.read_text().splitlines() if line.startswith("#")}


def links(path: Path):
    in_fence = False
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            for m in LINK_RE.finditer(CODE_SPAN_RE.sub("", line)):
                yield i, m.group(1)


def broken_links(root: Path) -> list[str]:
    errors = []
    for path in doc_files(root):
        if not path.is_file():
            continue
        for line, target in links(path):
            if re.match(r"[a-z]+:", target):  # http:, mailto:, ...
                continue
            file, _, frag = target.partition("#")
            dest = (path.parent / file).resolve() if file else path
            rel = path.relative_to(root)
            if not dest.exists():
                errors.append(f"{rel}:{line}: link '{target}' points to a missing file; fix the path, "
                              "or wrap the link in backticks if it's an example")
            elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                errors.append(f"{rel}:{line}: link '{target}' names no heading in {dest.name}; "
                              f"use one of its headings' anchors (lowercase, punctuation dropped, spaces as hyphens)")
    return errors


def test_repo_links_resolve():
    errors = broken_links(ROOT)
    assert not errors, "\n".join(errors)


def test_detects_missing_file_and_heading(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("# A\n\n## Some Rules (`x`)\n")
    (tmp_path / "AGENTS.md").write_text(
        "[ok](docs/a.md#some-rules-x) [gone](docs/b.md) [bad](docs/a.md#nope) [web](https://x.y)\n"
        "`[code](docs/b.md)`\n```\n[fenced](docs/b.md)\n```\n"
    )
    errors = broken_links(tmp_path)
    assert len(errors) == 2
    assert "docs/b.md" in errors[0] and "#nope" in errors[1]
