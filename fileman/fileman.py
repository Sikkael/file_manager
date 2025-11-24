"""This module provides the model-controller."""
# fileman/fileman.py

from pathlib import Path
from typing import Any, Dict, NamedTuple

from fileman.database import DatabaseHandler
from fileman.filehandler import *


class CurrentDirectory(NamedTuple):
    file: Dict[str, Any]
    error: int
    
class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        
    def add(self, dirname:str) -> CurrentDirectory:
        raise NotImplementedError("Method not implemented yet")