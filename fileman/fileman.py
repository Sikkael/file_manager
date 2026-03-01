"""This module provides the model-controller."""
# fileman/fileman.py

import configparser
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DEST_DIR_ERROR,  DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, DUPLICATE, FILE_HANDLING_ERROR, FILE_PROCESSING_ERRORS, JSON_ERROR, NEW, SUCCESS, DIR_ALREADY_ADDED_ERROR, config
from fileman.database import DatabaseHandler
from fileman.hashfiles import compute_file_hash

def get_destination_path(config_file: Path) -> Path:
    """Return the current path to the dest_directory."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["dest_directory"])

def write_log(message: str, log_file:str ="process.log", verbose:bool=False, append:bool=True)-> None:
    mode = 'a' if append else 'w'
    with open(log_file, mode) as log:
        log.write(message + "\n")
        if verbose:
            print(message)
        

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
    
    def __init__(self,latest_index,directories:List, files_stats:Dict[str, Any], files_metadata:Dict[str, Any]):
        self._latest_index = latest_index
        self._directories = directories
        self._files_stats = files_stats
        self._files_metadata = files_metadata
        self._destination_path = get_destination_path(config.CONFIG_FILE_PATH)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "latest_index": self._latest_index,
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
        dup_count = 0
        copy_count = 0
        for root, _, files in os.walk(dirname):
          for file_name in files:
                count += 1
                write_log(f"Processing file {count}: {file_name}", verbose=True)
                file_path = Path(os.path.join(root, file_name))
                
                h = compute_file_hash(file_path=file_path)
        
                if h not in self._files_metadata:
                    self._latest_index += 1
                    self._files_metadata[h] = {
                        "id": self._latest_index,
                        "file_path": str(file_path),
                        "parent":dirname,
                        "size": file_path.stat().st_size,
                        "created": time.ctime(os.path.getctime(file_path)),
                        "modified": time.ctime(os.path.getmtime(file_path)),
                        "hash": h,
                        "name": file_path.name,
                        "ext": file_path.suffix,
                        "duplicates": []
                        }
                    
                    _destination_path = resolve_path(self._destination_path, Path(file_path).suffix)
                    
                    try:
                        if _destination_path.joinpath(file_path.name).exists():
                           shutil.copy2(file_path, _destination_path.joinpath(f"{h}-{file_path.name}"))
                        else:
                           shutil.copy2(file_path, _destination_path)
                        copy_count += 1
                    except FILE_PROCESSING_ERRORS as e:
                        write_log(f"Error copying file {file_path}: {e}", "error.log")
                        return CurrentDirectory("", FILE_HANDLING_ERROR)
                    self._update_stats(self._files_metadata[h])
                    
                else:
                    dup_count += 1
                    write_log(f"Duplicate found: {file_path} and {self._files_metadata[h]['file_path']} have the same hash {h}", "dup.log", verbose=True)
                    if str(file_path) not in self._files_metadata[h]["duplicates"] and self._files_metadata[h]["file_path"] != str(file_path):
                       self._files_metadata[h]["duplicates"].append(str(file_path))
        write_log(f"Finished processing directory {dirname}. \nTotal files: {count} \nCopied: {copy_count} \nDuplicates: {dup_count}", "result.log", append=False)
        return CurrentDirectory(dirname, SUCCESS)       
                 
    
    def _update_stats(self, data:Dict[str, Any]) -> None:
        self._files_stats["total_files"] += 1
        self._files_stats["total_size"] += data["size"]
        if data["size"] > self._files_stats["biggest_file_size"]:
            self._files_stats["biggest_file_size"] = data["size"]
            self._files_stats["biggest_file"] = data["file_path"]
        if data["size"] < self._files_stats["smallest_file_size"]:
            self._files_stats["smallest_file_size"] = data["size"]
            self._files_stats["smallest_file"] = data["file_path"]
        if self._files_stats["total_files"] > 0:
            self._files_stats["average_file_size"] = self._files_stats["total_size"]//self._files_stats["total_files"]
        if data['ext'] not in self._files_stats['extensions']:
            self._files_stats['extensions'][data['ext']] = 1
        else:
            self._files_stats['extensions'][data['ext']] += 1
           
                
def init_files_handler(files_infos:Dict[str, Any]) -> FilesHandler:
    """Initialize the files handler."""
    return FilesHandler(latest_index=files_infos["latest_index"],directories=files_infos["directories"], 
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
        result = file_handler.add(dirname)
        if result.error != SUCCESS:
            return CurrentDirectory("", result.error)
        write = self._db_handler.write_file_data(file_handler.to_dict())
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
    
    def get_dir_list(self)-> List[Dict[str, Any]]:
        """List database directories."""
        dir_list = self._db_handler.read_file_data()
        return dir_list.file_infos   
