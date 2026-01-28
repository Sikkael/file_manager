"""This module provides the model-controller."""
# fileman/fileman.py

from pathlib import Path
import shutil
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DEST_DIR_ERROR, DIR_ERROR, JSON_ERROR, SUCCESS
from fileman.database import DatabaseHandler


def init_dest_dir(dest_path: Path) -> int:
    """Initialize the destination directory."""
    if dest_path.exists():
       return SUCCESS
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR

class CurrentDirectory(NamedTuple):
    dirname: str
    error: int


class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        self._files_infos = {}
        
    def add(self, dirname:str, _not_found_ok:bool) -> CurrentDirectory:
        """Add a new directory to the database."""
        if not Path(dirname).exists() and _not_found_ok == False:
           print("Directory does not exists.")
           return CurrentDirectory("", DIR_ERROR)
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        read.file_infos.append(dirname)
        write = self._db_handler.write_file_data(read.file_infos)
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
    
    def get_dir_list(self)-> List[Dict[str, Any]]:
        """List database directories."""
        dir_list = self._db_handler.read_file_data()
        return dir_list.file_infos   
   
        
  
    
    def set_dest_dir(self, dest_dir: Path) -> None:
        """Set the destination path."""
        if not dest_dir.exists():
           try:
               dest_dir.mkdir(parents=True, exist_ok=True)
               return CurrentDirectory(dirname=dest_dir.name, error=SUCCESS)
           except OSError:
               return CurrentDirectory(dirname=dest_dir.name, error=DEST_DIR_ERROR)
        else:
            # Directory exists, get the file data
            read = self._db_handler.read_file_data()
            if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
               return CurrentDirectory("", read.error)
        # No read errors, 
        files_infos = FilesInfos.from_dict(read.file_infos)
        files_infos.dest_directory = str(dest_dir)
        write = self._db_handler.write_file_data(files_infos)
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(str(dest_dir), SUCCESS)
