from abc import ABC, abstractmethod
import configparser
from pathlib import Path
import sys

from fileman import DB_WRITE_ERROR, DIR_ALREADY_ADDED_ERROR, DIR_NOT_FOUND_ERROR, SUCCESS, config
from fileman.database import DBResponse, DatabaseHandler
from fileman.directories import CurrentDirectory
from fileman.files_stats import FilesStats
from fileman.logger import write_log
from fileman.models import  BaseModel, Result
from typing import Generic, Type, TypeVar


T = TypeVar("T", bound=BaseModel)

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



class GenericRepository(Generic[T], ABC):
    
    @abstractmethod
    def add(self, entry: T)->Result:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_by_id(self, id:int) -> Result:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def update(self, entry: AbstractModel)->Result:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def delete_by_id(self, id: int)->Result:
        raise NotImplementedError("Subclasses must implement this method.")
    
    
    
class GenericJsonRepository(GenericRepository[T]):
    
    def __init__(self, db_handler: DatabaseHandler, model_cls: Type[T]):
        self._db_handler = db_handler
        self._model_cls = model_cls

    def add(self, entry: T) -> Result:
        """Add a new entry to the repository."""
        
        result = self._db_handler.add_entry(entry)
        if result is None:
            raise Exception("Failed to add entry to the database.")
        entry.id = result.id
        save_status = self._db_handler.save()
        if save_status != SUCCESS:
            return Result(error=DB_WRITE_ERROR, model=entry)
        return Result(error=SUCCESS, model=entry)
    
    def _retrieve_from_db(self, id: int) -> Result:
        
        db_response = self._db_handler.select(self._model_cls)
        
        
        return Result(error=SUCCESS, model=None)

    def get_by_id(self, id: int) -> Result:
        """Retrieve an entry by its ID."""
        db_response = self._db_handler.select(self._model_cls)
        if db_response.error != SUCCESS:
            return Result(error=db_response.error, model=None)
        
        entry_data = db_response.data.get(id)
        if entry_data is None:
            return Result(error=DIR_NOT_FOUND_ERROR, model=None)
        
        entry = self._model_cls(**entry_data)
        return Result(error=SUCCESS, model=entry)