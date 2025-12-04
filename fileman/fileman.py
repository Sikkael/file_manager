"""This module provides the model-controller."""
# fileman/fileman.py

from pathlib import Path
from typing import Any, Dict, NamedTuple

from fileman import DIR_ERROR
from fileman.database import DatabaseHandler
from fileman.filehandler import *


class CurrentDirectory(NamedTuple):
    dirname: str
    error: int
    
class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        
    def add(self, dirname:str, _not_found_ok:bool) -> CurrentDirectory:
        
        """Add a new directory to the database."""
        if not Path(dirname).exists() and _not_found_ok == False:
           print("Directory does not exists.")
           return CurrentDirectory("", DIR_ERROR)
        read = self._db_handler.read_file_data()
        if read.error == DIR_ERROR:
            return CurrentDirectory("", read.error)
        read.file_list.append(dirname)
        write = self._db_handler.write_file_data(read.file_list)
        return CurrentDirectory(dirname, write.error)