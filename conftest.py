import sys
from pathlib import Path

repo_root = Path(__file__).parent.resolve()
paths_to_add = [
    str(repo_root),
    str(repo_root / "person1"),
    str(repo_root / "person2"),
    str(repo_root / "person2" / "p2"),
    str(repo_root / "person3"),
    str(repo_root / "person4"),
    str(repo_root / "person4" / "app"),
]

for p in reversed(paths_to_add):
    if p not in sys.path:
        sys.path.insert(0, p)

