"""bump_version.py — increment the version string in setup.py.

Usage
-----
    python bump_version.py              # bump patch  (0.0.8 → 0.0.9)
    python bump_version.py --minor      # bump minor  (0.0.8 → 0.1.0)
    python bump_version.py --major      # bump major  (0.0.8 → 1.0.0)
    python bump_version.py --dry-run    # print what would change, write nothing

The script is intentionally self-contained (stdlib only) so it can run in
minimal CI environments without installing extra dependencies.
"""

import argparse
import re
import sys
from pathlib import Path

SETUP_PY = Path(__file__).parent / "setup.py"
VERSION_RE = re.compile(r'version="(\d+\.\d+\.\d+)"')


def increment_version(version: str, part: str = "patch") -> str:
    """Return a new version string with the requested part incremented.

    Lower-order parts are reset to zero when a higher-order part is bumped.

    Parameters
    ----------
    version:
        Current version in ``MAJOR.MINOR.PATCH`` format.
    part:
        Which component to increment: ``"major"``, ``"minor"``, or ``"patch"``.

    Returns
    -------
    str
        The incremented version string.

    Raises
    ------
    ValueError
        If *version* does not match ``MAJOR.MINOR.PATCH`` or *part* is unknown.
    """
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid version format: {version!r} (expected MAJOR.MINOR.PATCH)")

    major, minor, patch = map(int, parts)

    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unknown version part: {part!r} (expected 'major', 'minor', or 'patch')")


def update_setup_py(part: str = "patch", dry_run: bool = False) -> tuple[str, str]:
    """Read setup.py, bump the version, and write it back.

    Parameters
    ----------
    part:
        Which version component to increment (``"major"``, ``"minor"``, or ``"patch"``).
    dry_run:
        When ``True``, print what would change but do not write the file.

    Returns
    -------
    tuple[str, str]
        ``(old_version, new_version)`` as strings.

    Raises
    ------
    FileNotFoundError
        If ``setup.py`` does not exist at the expected location.
    ValueError
        If no ``version="..."`` line is found in ``setup.py``.
    """
    if not SETUP_PY.exists():
        raise FileNotFoundError(f"setup.py not found at {SETUP_PY}")

    content = SETUP_PY.read_text(encoding="utf-8")

    match = VERSION_RE.search(content)
    if not match:
        raise ValueError(f"No version string found in {SETUP_PY}")

    old_version = match.group(1)
    new_version = increment_version(old_version, part)
    new_content = VERSION_RE.sub(f'version="{new_version}"', content)

    if dry_run:
        print(f"[dry-run] Would update version: {old_version} → {new_version}")
    else:
        SETUP_PY.write_text(new_content, encoding="utf-8")
        print(f"Updated version: {old_version} → {new_version}")

    return old_version, new_version


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bump the package version in setup.py.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", action="store_true", help="Bump the major version component")
    group.add_argument("--minor", action="store_true", help="Bump the minor version component")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing the file",
    )
    args = parser.parse_args()

    part = "major" if args.major else "minor" if args.minor else "patch"

    try:
        update_setup_py(part=part, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
