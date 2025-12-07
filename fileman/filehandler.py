

import configparser
import hashlib
import os
from pathlib import Path

from fileman import DB_WRITE_ERROR, DEST_DIR_ERROR, SUCCESS


def init_dest_dir(dest_path: Path) -> int:
    """Create the database."""
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR
    
def get_dest_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["destination directory"])

def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def list_files_recursive(path:str, _files_infos:dict = dict())-> dict:
    _files_infos = {}
    count = 0
    duplicates = 0
    for root, _, files in os.walk(path):
        
        for file_name in files:
            count += 1
            print(f"Processing file {count}: {file_name}")
            file_path = os.path.join(root, file_name)
            h = compute_file_hash(file_path)    
            
            if h not in _files_infos:
                 _files_infos[h] = file_path
            else: 
                 print(f"Duplicate found: {file_path} and {_files_infos[h]} have the same hash {h}")
                 duplicates += 1
                 
    mess = f"Total files processed: {count}­\nTotal duplicates found: {duplicates}"
    print(mess)
    
    return _files_infos


class FilesHandler:
    """Class to handle file operations."""
    
    def __init__(self, dest_path: Path) -> None:
        self._files_infos = list_files_recursive(dest_path)
        
        
