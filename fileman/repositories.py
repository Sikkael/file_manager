from abc import ABC, abstractmethod
import configparser
from pathlib import Path
import sys
from typing import Any, Dict, List

from fileman import DB_WRITE_ERROR, DIR_ALREADY_ADDED_ERROR, DIR_NOT_FOUND_ERROR, SUCCESS, config
from fileman.database import DatabaseHandler
from fileman.directories import CurrentDirectory
from fileman.files_stats import FilesStats
from fileman.logger import write_log
from fileman.models import AbstractModel


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
        repository = GenericRepository(db_handler)
        repository.init()
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR

class GenericRepository(ABC):
    
    @abstractmethod
    def add(self, entry: AbstractModel)->AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_by_id(self, id:int) -> AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def update(self, entry: AbstractModel)->AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def delete_by_id(self, id: int)->bool:
        raise NotImplementedError("Subclasses must implement this method.")
    
    
    
class GenericJsonRepository(GenericRepository):
    
    def __init__(self, db_handler: DatabaseHandler):
        self._db_handler = db_handler
        
    def init(self)-> int:
        """Initialize the repository with blank data."""
        db_reponse = self._db_handler.write_file_data(__blank_file_infos__)
        if db_reponse.error != SUCCESS:
            return DB_WRITE_ERROR
        return SUCCESS