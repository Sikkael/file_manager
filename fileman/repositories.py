


import configparser
from pathlib import Path
import sys
from typing import Any, Dict, List

from fileman import DB_WRITE_ERROR, DIR_ALREADY_ADDED_ERROR, DIR_NOT_FOUND_ERROR, SUCCESS, config
from fileman.abstract_model import AbstractModel
from fileman.database import DatabaseHandler
from fileman.abstract_repository import AbstractRepository
from fileman.directories import CurrentDirectory
from fileman.files_stats import FilesStats
from fileman.logger import write_log


_blank_file_stats = {
    "total_files": 0, 
    "total_size": 0, 
    "biggest_file":"",
    "biggest_file_size":-sys.maxsize,
    "smallest_file":"",
    "smallest_file_size":sys.maxsize,
    "average_file_size":0,
    "exts": {},
    "oldest_file":"",
    "oldest_file_date":"Mon Feb  8 03:44:42 2100",
    "newest_file":"",
    "newest_file_date":"Mon Feb 3 03:44:42 1902",
    "duplicate_files_count":0,
    "highest_file_duplication_count":0,
    "most_duplicated_file":""

    }

__blank_file_infos__ = {
    "version": "1.0",
    "latest_index": 0,
    "parent_directories": [],
    "directories": [],
    "files_stats": _blank_file_stats,
    "files_metadata": {}
}


def init_repos(db_path: Path) -> int:
    """Create the repository.""" 
    try:
        db_handler = DatabaseHandler(db_path)
        repository = Repository(db_handler)
        repository.init()
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
    
class Repository(AbstractRepository):
    
    def __init__(self,db_handler: DatabaseHandler) -> None:
        self._db_handler = db_handler
    
    def add(self, model: AbstractModel) -> AbstractModel:
        # Implementation for adding a directory to the repository
        """Add a new directory to the database."""
        # Try to get dirname from database. If directory already
        # in database, return DIR_ALREADY_ADDED_ERROR
        # If directory does not exist, return DIR_NOT_FOUND_ERROR
        
        _dir_path = Path(dirname)
        if not _dir_path.exists():
           
           return DIR_NOT_FOUND_ERROR
        
        if dirname in self._directories:
           return DIR_ALREADY_ADDED_ERROR
        
        self._directories.append(str(_dir_path))    
           
        _top_dirs_ = self._parent_directories
        if len(_top_dirs_) == len([d for d in _top_dirs_ if not _dir_path.is_relative_to(d)]):
            self._parent_directories = [d for d in _top_dirs_ if not Path(d).is_relative_to(_dir_path)]
            self._parent_directories.append(str(_dir_path))
    
        write = self._db_handler.write_file_data({
            "latest_index": self._latest_index,
            "directories": self._directories,
            "parent_directories": self._parent_directories,
            "files_stats": self._files_stats.to_dict(),
            "files_metadata": self._files_metadata
        })
        
        if self._db_handler.copy_database() != SUCCESS:
            write_log(f"Error copying database to current directory.", "error.log", verbose=True)
        if write.error != SUCCESS:
            return CurrentDirectory("", write.error)
        return CurrentDirectory(dirname, write.error)
    
    def get(self, item_id: Any) -> AbstractModel:
        # Implementation for retrieving directories from the repository
        return AbstractModel()
    
    def update(self, item: AbstractModel) -> AbstractModel:
        # Implementation for updating a directory in the repository
        return AbstractModel()
    
    def delete(self, item: AbstractModel) -> bool:
        # Implementation for deleting a directory from the repository
        return False

    def init(self)-> int:
        """Initialize the repository with blank data."""
        db_reponse = self._db_handler.write_file_data(__blank_file_infos__)
        if db_reponse.error != SUCCESS:
            return DB_WRITE_ERROR
        return SUCCESS