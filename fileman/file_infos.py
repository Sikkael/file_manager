

import configparser
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

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

def build_dest_dir(dest_path: Path)-> None:
    """Build the destination directory structure."""
    for root, _, files in os.walk(dest_path):
        
        for file_name in files:  
            print(f"File: {file_name} in {root}")
    
class FilesStats(NamedTuple):
    total_files: int
    total_size: int
    max_file_size: int
    min_file_size: int
    newest_file: str
    oldest_file: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files": self.total_files,
            "total_size": self.total_size,
            "max_file_size": self.max_file_size,
            "min_file_size": self.min_file_size,
            "newest_file": self.newest_file,
            "oldest_file": self.oldest_file,
        }
        
    def from_dict(data: Dict[str, Any]) -> 'FilesStats':
        return FilesStats(
            total_files=data.get("total_files", 0),
            total_size=data.get("total_size", 0),
            max_file_size=data.get("max_file_size", 0),
            min_file_size=data.get("min_file_size", 0),
            newest_file=data.get("newest_file", ""),
            oldest_file=data.get("oldest_file", ""),
        )
        
class FilesData(NamedTuple):
    file_path: str
    file_size: int
    file_hash: str
    created_at: str
    modified_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }
        
    def from_dict(data: Dict[str, Any]) -> 'FilesData':
        return FilesData(
            file_path=data.get("file_path", ""),
            file_size=data.get("file_size", 0),
            file_hash=data.get("file_hash", ""),
            created_at=data.get("created_at", ""),
            modified_at=data.get("modified_at", ""),
        )
class FilesInfos(NamedTuple):
    directories: List[str]
    dest_directory: str
    files_stats:FilesStats
    files_data: FilesData
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "directories": self.directories,
            "dest_directory": self.dest_directory,
            "files_stats": self.files_stats.to_dict(),
            "files_data": self.files_data.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilesInfos':
        return FilesInfos(
            directories=data.get("directories", []),
            dest_directory=data.get("dest_directory", ""),
            files_stats=FilesStats.from_dict(data.get("files_stats", {})),
            files_data=FilesData.from_dict(data.get("files_data", {})),
        )


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


if __name__ == "__main__":
    build_dest_dir(DEFAULT_DEST_FOLDER_PATH)        