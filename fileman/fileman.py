"""This module provides the model-controller."""
# fileman/fileman.py

from pathlib import Path
import shutil
from typing import Any, Dict, List, NamedTuple

from fileman import DIR_ERROR
from fileman.database import DatabaseHandler
from fileman.filehandler import *


class CurrentDirectory(NamedTuple):
    dirname: str
    error: int
    
class FileManager:
    
    def __init__(self, db_path: Path,dest_path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        self._dest_path = dest_path
        self._files_infos = {}
        
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
    
    def get_dir_list(self)-> List[Dict[str, Any]]:
        """List database directories."""
        dir_list = self._db_handler.read_file_data()
        return dir_list.file_list   
    
    def get_files_infos(self) -> Dict:
        """Get the files information."""
        return FilesHandler(self._dest_path).get_files_infos()
    
    def update_files(self, _folder: Path) -> None:
        """Update the files information."""
        self._files_infos = list_files_recursive(self._dest_path, self._files_infos)
        self._save_files(_folder)
        
    def _save_files(self, _folder) -> None:
        """Save the files to destination folders."""
        _files_infos = list_files_recursive(_folder, self._files_infos)
        for hash_value, file_path in _files_infos.items():
            dest_path = os.path.join(self._dest_path, os.path.basename(file_path))
            if not os.path.exists(dest_path):
               shutil.copy2(file_path, dest_path)
               print(f"Copied {file_path} to {dest_path}")
               print(f"hashed {hash_value}")
            else:
               print(f"File {dest_path} already exists. Skipping copy.")
        