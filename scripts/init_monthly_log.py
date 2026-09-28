"""Create a blank monthly log (`YYYY-MM/LOG.md`) for a given YYYY-MM."""

import argparse
import calendar
from pathlib import Path


DAY_ABBREVS = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def parse_month(value: str) -> tuple[int, int]:
    """Validate and parse a YYYY-MM string into (year, month)."""
    parts = value.split("-")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"invalid month '{value}'. Expected YYYY-MM (e.g., 2026-04)")
    try:
        year, month = int(parts[0]), int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid month '{value}'. Expected YYYY-MM (e.g., 2026-04)")
    if month < 1 or month > 12:
        raise argparse.ArgumentTypeError(f"invalid month '{value}'. Expected YYYY-MM (e.g., 2026-04)")
    return year, month


def generate(year: int, month: int) -> str:
    month_name = MONTH_NAMES[month - 1]
    num_days = calendar.monthrange(year, month)[1]

    lines = [f"# {month_name} {year}", "", "**Calendar:**", ""]

    for day in range(1, num_days + 1):
        # weekday(): Monday=0, Sunday=6
        dow = calendar.weekday(year, month, day)
        lines.append(f"{day} {DAY_ABBREVS[dow]}")

    lines.extend(["", "**Tasks:**", ""])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Create a blank monthly log.")
    parser.add_argument("month", type=parse_month, help="month in YYYY-MM format (e.g., 2026-04)")
    parser.add_argument(
        "--output-root", type=str, default=None,
        help="Override output root directory (default: repo root next to scripts/)",
    )
    args = parser.parse_args()

    year, month = args.month
    output_root = Path(args.output_root) if args.output_root else Path(__file__).resolve().parent.parent
    month_dir = output_root / f"{year:04d}-{month:02d}"
    month_dir.mkdir(parents=True, exist_ok=True)
    out_path = month_dir / "LOG.md"
    if out_path.exists():
        # Never regenerate: the existing log may hold entries from other sessions.
        parser.error(f"{out_path} already exists; edit it with the Edit tool instead")
    out_path.write_text(generate(year, month))
    print(out_path)


if __name__ == "__main__":
    main()
