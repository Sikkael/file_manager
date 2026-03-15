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
from fileman.database import DatabaseHandler,__blank_file_infos__
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
        

def resolve_path(path: str, fname:Path) -> Path:
    _pth = os.path.join(path, fname.suffix)
    if not os.path.exists(_pth):
       os.makedirs(_pth)
    f_path = Path(os.path.join(_pth, fname.name)) 
    return f_path if not f_path.exists() else Path(os.path.join(_pth, f"{compute_file_hash(fname)}-{fname.name}"))
    
         
    
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
    
    def __init__(self,latest_index,directories:List,parent_directories:List, files_stats:Dict[str, Any], files_metadata:Dict[str, Any]):
        self._latest_index = latest_index
        self._directories = directories
        self._parent_directories = parent_directories
        self._files_stats = files_stats
        self._files_metadata = files_metadata
        self._destination_path = get_destination_path(config.CONFIG_FILE_PATH)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "latest_index": self._latest_index,
            "directories": self._directories,
            "parent_directories": self._parent_directories,
            "files_stats": self._files_stats,
            "files_metadata": self._files_metadata
        }
    
    def _add_directory(self, dirname:str) -> int:
        """Add a new directory to the database."""
        if not Path(dirname).exists():
           write_log(f"This directory does not exists --> {dirname}", "error.log")
           return DIR_NOT_FOUND_ERROR
        
        if dirname in self._directories:
           return DIR_ALREADY_ADDED_ERROR
        
        self._directories.append(dirname)    
           
        _top_dirs_ = self._parent_directories
        if len(_top_dirs_) == len([d for d in _top_dirs_ if not Path(dirname).is_relative_to(d)]):
            self._parent_directories = [d for d in _top_dirs_ if not Path(d).is_relative_to(dirname)]
            self._parent_directories.append(dirname)
        
        return SUCCESS
    
    def _process_directory(self, dirname: Path) -> int:
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
                    _destination_path = resolve_path(self._destination_path, 
                        file_path)
                    self._latest_index += 1
                    self._files_metadata[h] = {
                        "id": self._latest_index,
                        "file_path": str(file_path),
                        "parent":str(dirname),
                        "size": file_path.stat().st_size,
                        "created": time.ctime(os.path.getctime(file_path)),
                        "modified": time.ctime(os.path.getmtime(file_path)),
                        "hash": h,
                        "name": _destination_path.name,
                        "ext": file_path.suffix,
                        "duplicates": []
                        }
                
                    
                    try:
                        assert not _destination_path.exists(), f"Destination file {str(_destination_path)} already exists."
                        shutil.copy2(file_path, _destination_path)
                        write_log(f"File copied successfully: {file_path} -> {_destination_path}", "copy.log")
                        copy_count += 1
                    except FILE_PROCESSING_ERRORS as e:
                        write_log(f"Error copying file {file_path}: {e}", "error.log")
                        return FILE_HANDLING_ERROR
                    self._update_stats(self._files_metadata[h])
                    
                else:
                    dup_count += 1
                    write_log(f"Duplicate found: {file_path} and {self._files_metadata[h]['file_path']} have the same hash {h}", "dup.log", verbose=True)
                    if str(file_path) not in self._files_metadata[h]["duplicates"] and self._files_metadata[h]["file_path"] != str(file_path):
                       self._files_metadata[h]["duplicates"].append(str(file_path))
        self._final_stats()
        write_log(f"Finished processing directory {dirname}. \nTotal files: {count} \nCopied: {copy_count} \nDuplicates: {dup_count}", "result.log", append=False)
        return SUCCESS       
        
    def add(self, dirname:str)-> int:
        """Add a new directory to the database."""
        dir_code = self._add_directory(dirname)
        if dir_code != SUCCESS:
            return dir_code
        process_code = self._process_directory(Path(dirname))
        if process_code != SUCCESS:
            return process_code
        return SUCCESS       
    
    def update_all(self) -> int:
        """Update all directories in the database."""
        for dirname in self._parent_directories:
            process_code = self._process_directory(Path(dirname))
            if process_code != SUCCESS:
                return process_code
        return SUCCESS
    
    def _update_stats(self, data:Dict[str, Any]) -> None:
        
        self._files_stats["total_size"] += data["size"]
        if data["size"] > self._files_stats["biggest_file_size"]:
            self._files_stats["biggest_file_size"] = data["size"]
            self._files_stats["biggest_file"] = data["file_path"]
        if data["size"] < self._files_stats["smallest_file_size"]:
            self._files_stats["smallest_file_size"] = data["size"]
            self._files_stats["smallest_file"] = data["file_path"]
        
        if data['ext'] not in self._files_stats['extensions']:
            self._files_stats['extensions'][data['ext']] = 1
        else:
            self._files_stats['extensions'][data['ext']] += 1
    
                
    def _final_stats(self) -> None:
        """Calculate final statistics after processing all files."""
        self._files_stats["total_files"] = len(self._files_metadata)
        if self._files_stats["total_files"] > 0:
            self._files_stats["average_file_size"] = self._files_stats["total_size"]//self._files_stats["total_files"]
        
    def get_directories(self) -> List[Dict[str, Any]]:
        """Return the list of directories in the database."""
        return self._directories
        
        
def init_files_handler(files_infos:Dict[str, Any]) -> FilesHandler:
    """Initialize the files handler."""
    return FilesHandler(latest_index=files_infos["latest_index"],directories=files_infos["directories"], 
                        parent_directories=files_infos["parent_directories"],
                        files_stats= files_infos["files_stats"], 
                        files_metadata=files_infos["files_metadata"])
class CurrentDirectory(NamedTuple):
    dirname: str
    error: int


class FileManager:
    
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)
        self._files_infos = {}
        
    def add_directory(self, dirname:str) -> CurrentDirectory:
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        
        # initailize the files handler with the data from the database 
        file_handler = init_files_handler(read.files_infos)
        result_code = file_handler.add(dirname)
        if result_code != SUCCESS:
            return CurrentDirectory("", result_code)
        write = self._db_handler.write_file_data(file_handler.to_dict())
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
        
    def add(self, dirname:str) -> CurrentDirectory:
        
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        
        # initailize the files handler with the data from the database 
        file_handler = init_files_handler(read.files_infos)
        result_code = file_handler.add(dirname)
        if result_code != SUCCESS:
            return CurrentDirectory("", result_code)
        write = self._db_handler.write_file_data(file_handler.to_dict())
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
    
    def update_all(self) -> CurrentDirectory:
        """Update all directories in the database."""
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        
        # initailize the files handler with the data from the database 
        file_handler = init_files_handler(read.files_infos)
        result_code = file_handler.update_all()
        if result_code != SUCCESS:
                return CurrentDirectory("", result_code)
        write = self._db_handler.write_file_data(file_handler.to_dict())
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory("All directories updated successfully.", write.error)
    
    def clear(self) -> CurrentDirectory:
        """Clean the database and the destination directory."""
        dest_path = get_destination_path(config.CONFIG_FILE_PATH)
        try:
            if dest_path.exists():
                shutil.rmtree(dest_path)
            init_dest_dir(dest_path)
            self._db_handler.write_file_data(__blank_file_infos__)
            logfs = ("process.log", "error.log", "dup.log", "result.log")
            for logf in logfs:
                if Path(logf).exists():
                    Path(logf).unlink()
            return CurrentDirectory("", SUCCESS)
        except OSError as e:
            write_log(f"Error cleaning destination directory: {e}", "error.log")
            return CurrentDirectory("", DEST_DIR_ERROR)
    
    def get_dir_list(self)-> List[Dict[str, Any]]:
        """List database directories."""
        read = self._db_handler.read_file_data()
        if read.error == JSON_ERROR or read.error == DB_READ_ERROR:
            return CurrentDirectory("", read.error)
        file_handler = init_files_handler(read.files_infos)
        return file_handler.get_directories()