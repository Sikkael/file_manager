"""This module provides the model-controller."""
# fileman/fileman.py

import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR,  DIR_ERROR, DIR_EXIST_ERROR, JSON_ERROR, SUCCESS
from fileman.database import DatabaseHandler
from fileman.hashfiles import compute_file_hash



def write_log(message: str, log_file="process.log")-> None:
    with open(log_file, 'a') as log:
        log.write(message + "\n")
        
def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information."""
    return {
        "file: ": file_path,
        "size": os.path.getsize(file_path),
        "created": time.ctime(os.path.getctime(file_path)),
        "modified": time.ctime(os.path.getmtime(file_path)),
    }

def list_files_recursive(path=".")-> dict:
    files_paths = {}
    count = 0
    duplicates = 0
    for root, _, files in os.walk(path):
        
        for file_name in files:
            count += 1
            print(f"Processing file {count}: {file_name}")
            file_path = os.path.join(root, file_name)
            h = compute_file_hash(file_path)    
            
            if h not in files_paths:
                 files_paths[h] = get_file_info(file_path)
                 print(f"File: {file_path}")
                 print(f"Size (bytes): {os.path.getsize(file_path)}")
                 print(f"Created: {time.ctime(os.path.getctime(file_path))}")
                 print(f"Modified: {time.ctime(os.path.getmtime(file_path))}")
            else: 
                 print(f"Duplicate found: {file_path} and {files_paths[h]} have the same hash {h}")
                 duplicates += 1
                 write_log(f"Duplicate found: {file_path} and {files_paths[h]} have the same hash {h}")
                 
    mess = f"Total files processed: {count}­\nTotal duplicates found: {duplicates}"
    print(mess)
    write_log(mess,"count.log")
    
    return files_paths


def init_dest_dir(dest_path: Path) -> int:
    """Initialize the destination directory."""
    if dest_path.exists():
       return DIR_EXIST_ERROR
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR


class FilesStats:
    def __init__(self, total_files: int = 0, total_size: int = 0, max_size:int = (-sys.maxsize), min_size:int = sys.maxsize) -> None:
        self._total_files = total_files
        self._total_size = total_size
        self._max_size = max_size
        self._min_size = min_size
        self._avg_size = 0
        self._biggest_file = None
        self._smallest_file = None
        

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
        if not dirname in read.file_infos["directories"]:
            read.file_infos["directories"].append(dirname)
        files_infos = read.file_infos["file_infos"]
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
           except OSError:
               return CurrentDirectory(dirname=dest_dir.name, error=DEST_DIR_ERROR)
        else:
            # Directory exists, get the file data
            read = self._db_handler.read_file_data()
            
            
            if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
               return CurrentDirectory("", read.error)
        # No read errors, 
        
        read.file_infos["dest_directory"] = str(dest_dir)
        read.file_infos["files_data"] = list_files_recursive(dest_dir)
        write = self._db_handler.write_file_data(read.file_infos)
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(str(dest_dir), SUCCESS)
