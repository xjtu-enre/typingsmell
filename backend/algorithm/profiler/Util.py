import os
from pathlib import Path
from typing import Optional


def find(name: str, dir: Optional[Path]) -> Optional[Path]:
    if dir is not None:
        for entry in os.scandir(dir):
            if entry.name == name:
                return dir.joinpath(name)
    return None
