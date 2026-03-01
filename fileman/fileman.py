"""This module provides the model-controller."""
# fileman/fileman.py

import configparser
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DEST_DIR_ERROR,  DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, DUPLICATE, JSON_ERROR, NEW, SUCCESS, DIR_ALREADY_ADDED_ERROR, config
from fileman.database import DatabaseHandler
from fileman.hashfiles import compute_file_hash

def get_destination_path(config_file: Path) -> Path:
    """Return the current path to the dest_directory."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    print(config_parser["General"]["dest_directory"])
    return Path(config_parser["General"]["dest_directory"])

def write_log(message: str, log_file:str ="process.log", verbose:bool=False)-> None:
    with open(log_file, 'a') as log:
        log.write(message + "\n")
        if verbose:
            print(message)
        
def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file information."""
    return {
        "file_path: ": file_path,
        "size": os.path.getsize(file_path),
        "created": time.ctime(os.path.getctime(file_path)),
        "modified": time.ctime(os.path.getmtime(file_path)),
    }
    
class FileMetadata:
    file_path: str
    size: int
    created: str
    modified: str
    name: str
    hash: str
    ext: str
    duplicates: List[str]

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

def resolve_path(path: str, ext:str) -> Path:
    _pth = os.path.join(path, ext)
    if not os.path.exists(_pth):
       os.makedirs(_pth)
    return Path(_pth)
         
    
    

def init_dest_dir(dest_path: Path) -> int:
    """Initialize the destination directory."""
    if dest_path.exists():
       return DIR_EXIST_ERROR
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR


class FilesHandler:
    
    def __init__(self,directories:List, files_stats:Dict[str, Any], files_metadata:Dict[str, Any]):
        self._directories = directories
        self._files_stats = files_stats
        self._files_metadata = files_metadata
        
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "directories": self._directories,
            "files_stats": self._files_stats,
            "files_metadata": self._files_metadata
        }
    
    def add(self, dirname:str):
        """Add a new directory to the database."""
        if not Path(dirname).exists():
           write_log(f"This directory does not exists --> {dirname}", "error.log")
           return CurrentDirectory("", DIR_NOT_FOUND_ERROR)
        
        if dirname in self._directories:
           return CurrentDirectory("", DIR_ALREADY_ADDED_ERROR)
        # add the directory and the file data to files_infos
        self._directories.append(dirname)
        count = 0
        for root, _, files in os.walk(dirname):
          for file_name in files:
                count += 1
                # write_log(f"Processing file {count}: {file_name}", verbose=True)
                files_path = os.path.join(root, file_name)
                if self._update_metadata(Path(files_path)) == NEW:
                   
                   _destination_path = resolve_path(get_destination_path(config.CONFIG_FILE_PATH), Path(files_path).suffix)
                   
                   shutil.copy2(files_path, _destination_path)  
                
    def _update_metadata(self, file_path):
        
        h = compute_file_hash(file_path=file_path)
        
        if h not in self._files_metadata:
           
           self._files_metadata[h] = {
               "file_path": str(file_path),
               "size": file_path.stat().st_size,
               "created": time.ctime(os.path.getctime(file_path)),
               "modified": time.ctime(os.path.getmtime(file_path)),
               "hash": h,
               "name": file_path.name,
               "ext": file_path.suffix,
               "duplicates": []
               }
            
           return NEW
            
        else:
            
            write_log(f"Duplicate found: {file_path} and {self._files_metadata[h]['file_path']} have the same hash {h}", "dup.log")
            if str(file_path) not in self._files_metadata[h]["duplicates"]:
                self._files_metadata[h]["duplicates"].append(str(file_path))
                
            return DUPLICATE
           
                
def init_files_handler(files_infos:Dict[str, Any]) -> FilesHandler:
    """Initialize the files handler."""
    return FilesHandler(directories=files_infos["directories"], 
                        files_stats= files_infos["files_stats"], 
                        files_metadata=files_infos["files_metadata"])
class CurrentDirectory(NamedTuple):
    dirname: str
    error: int


class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        self._files_infos = {}
        
    def add(self, dirname:str) -> CurrentDirectory:
        """Add a new directory to the database."""
        if not Path(dirname).exists():
           write_log(f"This directory does not exists --> {dirname}", "error.log")
           return CurrentDirectory("", DIR_NOT_FOUND_ERROR)
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        
        files_infos = read.files_infos
        
        
        if dirname in files_infos["directories"]:
           return CurrentDirectory("", DIR_ALREADY_ADDED_ERROR)
        # add the directory and the file data to files_infos
        
        file_handler = init_files_handler(files_infos)
        file_handler.add(dirname)
        write = self._db_handler.write_file_data(file_handler.to_dict())
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
    
    def get_dir_list(self)-> List[Dict[str, Any]]:
        """List database directories."""
        dir_list = self._db_handler.read_file_data()
        return dir_list.file_infos   
