from abc import ABC, abstractmethod
import configparser
from pathlib import Path
import sys

from fileman import DB_WRITE_ERROR, DIR_ALREADY_ADDED_ERROR, DIR_NOT_FOUND_ERROR, SUCCESS, config
from fileman.database import DBResponse, DatabaseHandler
from fileman.directories import CurrentDirectory
from fileman.files_stats import FilesStats
from fileman.logger import write_log
from fileman.models import  BaseModel, Collection, Directory, Result
from typing import Generic, List, Optional, Type, TypeVar




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


T = TypeVar("T", bound=BaseModel)
class GenericRepository(Generic[T], ABC):
    
    @abstractmethod
    def add(self, entry: T)->Result:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_by_id(self, id:int) -> Result:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def update(self, entry:T)->Result:
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
        
        db_response = self._db_handler.select(self._model_cls, int(id))
        
        if db_response.error != SUCCESS:
            return Result(error=db_response.error, model=None)
        model = self._model_cls(**db_response.data)
        return Result(error=SUCCESS, model=model)
        
    def get_by_id(self, id: int) -> Result:
        """Retrieve an entry by its ID."""
        return self._retrieve_from_db(id)
    
    
    def update(self, entry: T) -> Result:
        """Update an existing entry in the repository."""
        
        # Update the entry in the database
        updated_entry = self._db_handler.add_entry(entry)  # This will overwrite the existing entry
        save_status = self._db_handler.save()
        if save_status != SUCCESS:
            return Result(error=DB_WRITE_ERROR, model=updated_entry)
        
        return Result(error=SUCCESS, model=entry)
    
    def _construct_lst_from_db(self) -> List[T]:
        """Retrieve all entries of the model class from the database."""
        db_response = self._db_handler.select_all(self._model_cls, None)  # Assuming None retrieves all entries
        if db_response.error != SUCCESS:
            return []
        return [self._model_cls(**data) for data in db_response.data.values()]
        
        
    def list(self) -> Result:
        """List entries in the repository based on filters."""
        entries = Collection(lst=self._construct_lst_from_db())
        
        # I will apply filters here eventually
        ''''' Apply filters here'''
        
        return Result(error=SUCCESS, model=entries)
    
    def delete_by_id(self, id: int) -> Result:
        """Delete an entry by its ID."""
        db_code = self._db_handler.delete_entry(self._model_cls, id)
        if db_code != SUCCESS:
            return Result(error=db_code, model=None)
        
        save_status = self._db_handler.save()
        
        if save_status != SUCCESS:
            return Result(error=DB_WRITE_ERROR, model=None)
        
        return Result(error=SUCCESS, model=None)

class DirectoryReposityBase(GenericRepository[Directory], ABC):
    """Directory repository.
    """
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Directory]:
        raise NotImplementedError()
    
class DirectoryReposity(GenericJsonRepository[Directory],DirectoryReposityBase):
    """Directory repository.
    """
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__(db_handler, Directory)
    
    def get_by_pathname(self, name: str) -> Result:
        """Retrieve a directory by its name."""
        db_response = self._db_handler.select_all(Directory, lambda d: d.get('dirname') == name)
        
        if db_response.error != SUCCESS or not db_response.data:
            return Result(error=DIR_NOT_FOUND_ERROR, model=None)
        
        # Assuming only one directory with the given name exists
        dir_data = next(iter(db_response.data.values()))
        directory = Directory(**dir_data)
        return Result(error=SUCCESS, model=directory)
    