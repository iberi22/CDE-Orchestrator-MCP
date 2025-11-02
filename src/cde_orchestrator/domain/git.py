# src/cde_orchestrator/domain/git.py

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

@dataclass
class Modification:
    change_type: str  # e.g., 'A' for added, 'M' for modified, 'D' for deleted, 'R' for renamed
    old_path: Path
    new_path: Path

@dataclass
class Commit:
    hash: str
    author: str
    date: datetime
    message: str
    modifications: List[Modification] = field(default_factory=list)
