

import configparser
import hashlib
import json
import os
from pathlib import Path
from typing import Dict

from fileman import DEST_DIR_ERROR, SUCCESS

DEFAULT_DEST_FOLDER_PATH = Path(os.path.expanduser("~/fileman"))



def init_dest_dir(dest_path: Path) -> int:
    """Create the database."""
    try:
        if dest_path.exists():
           d = list_files_recursive(dest_path)
           print(f"Destination folder {dest_path} already exists with {len(d)} files.")
           return SUCCESS
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR
    
def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def write_log(message: str, log_file="process.log")-> None:
    with open(log_file, 'a') as log:
        log.write(message + "\n")

def list_files_recursive(path:str, _files_infos:dict = {})-> dict:
    
    count = 0
    duplicates = 0
    for root, _, files in os.walk(path):
        
        for file_name in files:
            count += 1
            mess = f"Processing file {count}: {file_name}"
            write_log(mess)
            print(mess)
            file_path = os.path.join(root, file_name)
            h = compute_file_hash(file_path)    
            
            if h not in _files_infos:
                 _files_infos[h] = file_path
            else: 
                 print(f"Duplicate found: {file_path} and {_files_infos[h]} have the same hash {h}")
                 duplicates += 1
                 
    mess = f"Total files processed: {len(_files_infos)}­\nTotal duplicates found: {duplicates}"
    write_log(mess)
    print(mess)
    
    return _files_infos

class FileInfos:
    """Class to store file information."""
    
    def __init__(self, file_path: Path, hash_value: str) -> None:
        self.file_path = file_path
        self.hash_value = hash_value


class FilesHandler:
    """Class to handle file operations."""
    
    def __init__(self, dest_path: Path) -> None:
        self._files_infos:Dict = list_files_recursive(dest_path)
        
        
    def get_files_infos(self) -> Dict:
        """Get the files information."""
        return self._files_infos
    
    def update_files_infos(self, _folder: Path) -> None:
        """Update the files information."""
        _files_infos = self._files_infos
        self._files_infos = list_files_recursive(_folder, _files_infos)
        