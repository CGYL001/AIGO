import shutil
from pathlib import Path
import datetime
import re

"""relocate_tests.py

Script to unify all test files under a single `tests/` hierarchy.

• Unit tests  -> tests/unit/
• Integration tests -> tests/integration/

Heuristics:
  - Files/dirs containing `integration` in their path/name are treated as integration.
  - Otherwise default to unit tests.

Existing paths are COPIED, not moved, so original data remains for manual cleanup.
A mapping file `tests/moved_tests_<timestamp>.txt` records source -> target.
"""

ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = ROOT / "tests"
UNIT_DIR = TEST_ROOT / "unit"
INT_DIR = TEST_ROOT / "integration"


def ensure(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)


def is_integration(path: Path) -> bool:
    return "integration" in path.parts or "e2e" in path.parts or "demo" in path.name


def main():
    ensure(UNIT_DIR)
    ensure(INT_DIR)
    moved_log = TEST_ROOT / f"moved_tests_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with moved_log.open("w", encoding="utf-8") as log:
        # Find candidate test files/dirs
        for p in ROOT.glob("**/test*_*.py"):
            # skip already in new structure
            if TEST_ROOT in p.parents:
                continue
            target_base = INT_DIR if is_integration(p) else UNIT_DIR
            target = target_base / p.name
            ensure(target.parent)
            shutil.copy2(p, target)
            log.write(f"{p.relative_to(ROOT)} -> {target.relative_to(ROOT)}\n")
            print(f"[+] Copied {p} -> {target}")
        # Also migrate directories starting with test_*
        for d in ROOT.glob("test_*"):
            if not d.is_dir() or TEST_ROOT in d.parents:
                continue
            dest_dir = INT_DIR / d.name if is_integration(d) else UNIT_DIR / d.name
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(d, dest_dir)
            log.write(f"{d.relative_to(ROOT)} -> {dest_dir.relative_to(ROOT)}\n")
            print(f"[+] Copied {d} -> {dest_dir}")
    print(f"\n[✓] Test relocation finished. See log: {moved_log.relative_to(ROOT)}")


if __name__ == "__main__":
    main() 