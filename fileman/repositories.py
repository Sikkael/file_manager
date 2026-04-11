


from pathlib import Path
import sys

from fileman import DB_WRITE_ERROR, SUCCESS
from fileman.database import DatabaseHandler
from fileman.irepository import AbstractRepository

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
        repository.add(__blank_file_infos__)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
    
class Repository(AbstractRepository):
    
    def __init__(self, db_handler):
        self._db_handler = db_handler
    
    def add(self, item):
        # Implementation for adding a directory to the repository
        pass
    
    def get(self):
        # Implementation for retrieving directories from the repository
        pass
    
    def update(self, item):
        # Implementation for updating a directory in the repository
        pass
    
    def delete(self, item):
        # Implementation for deleting a directory from the repository
        pass

