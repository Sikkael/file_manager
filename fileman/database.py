"""This module provides the database functionality."""
# fileman/database.py

import configparser
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS


DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_fileman.json"
)

_file_stats = {
    "total_files": 0, 
    "total_size": 0, 
    "biggest_file":"",
    "biggest_file_size":-sys.maxsize,
    "smallest_file":"",
    "smallest_file_size":sys.maxsize,
    "average_file_size":0,
    "extensions": {},
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
    "files_stats": _file_stats,
    "files_metadata": {}
}

def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """Create the database.""" 
    try:
        with db_path.open("w") as db:
           json.dump(__blank_file_infos__, db, indent=4)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DBResponse(NamedTuple):
    files_infos: Dict[str, Any]
    error: int

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_file_data(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse({}, JSON_ERROR)
        except OSError:  # Catch file IO problems
            return DBResponse({}, DB_READ_ERROR)

    def write_file_data(self, files_infos: Dict[str,Any]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(files_infos, db, indent=4)
            return DBResponse(files_infos, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(files_infos, DB_WRITE_ERROR)
        
    def copy_database(self) -> int:
        try:
            shutil.copy2(self._db_path, Path.cwd())
            return SUCCESS
        except OSError:  # Catch file IO problems
            return DB_READ_ERROR
        
        