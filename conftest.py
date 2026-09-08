import sys
from pathlib import Path

repo_root = Path(__file__).parent.resolve()
for folder in ["person1", "person2", "person3", "person4"]:
    folder_path = str(repo_root / folder)
    if folder_path not in sys.path:
        sys.path.insert(0, folder_path)
