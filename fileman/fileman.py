"""This module provides the model-controller."""
# fileman/fileman.py

from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from fileman.database import DatabaseHandler
from fileman.filehandler import *


class CurrentFile(NamedTuple):
    file: Dict[str, Any]
    error: int
    
class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        
    def add(self, description: List[str], filename:str) -> CurrentFile:
        raise NotImplementedError("Method not implemented yet")