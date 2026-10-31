"""Packs the executable and the README into one archive.

Usage: python package.py <path to executable> <archive name without extension>

Windows gets a .zip, Linux and macOS get a .tar.gz, because a tar archive keeps the
executable permission that a plain download would lose.
"""

import sys
import tarfile
import zipfile
from pathlib import Path


def main():
    exe = Path(sys.argv[1])
    name = sys.argv[2]
    readme = Path("README.md")

    if not exe.exists():
        sys.exit(f"Executable not found: {exe}")

    files = [exe] + ([readme] if readme.exists() else [])

    if exe.suffix == ".exe":
        archive = Path(f"{name}.zip")

        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(f, f"{name}/{f.name}")

    else:
        archive = Path(f"{name}.tar.gz")

        with tarfile.open(archive, "w:gz") as t:
            for f in files:
                t.add(f, f"{name}/{f.name}")

    print(f"Created {archive} ({archive.stat().st_size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
