"""This module provides the database functionality."""
# fileman/database.py

import configparser
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS
from fileman.models import AbstractModel


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


class DBResponse(NamedTuple):
    files_infos: Dict[str, Any]
    error: int

class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        
        if not db_path.exists():
            raise DatabaseError(f"Database file does not exist: {db_path}")
        
        self._db_path = db_path
        self._data_ = {}
        
    def load_database(self) -> None:
        """Load the database from the JSON file."""
        try:
            with self._db_path.open("r") as db:
                try:
                    self._data_ = json.load(db)
                    
                except json.JSONDecodeError:  # Catch wrong JSON format
                    raise DatabaseError(f"Invalid JSON format in database file: {self._db_path}")
        except OSError:  # Catch file IO problems
            raise DatabaseError(f"Error reading database file: {self._db_path}")
        
    def read_file_data(self) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse({}, JSON_ERROR)
        except OSError:  # Catch file IO problems
            return DBResponse({}, DB_READ_ERROR)

    def add_entry(self, entry: AbstractModel) -> AbstractModel:
        """Add a new entry to the database."""
        

        return entry  # Return the newly added entry with its ID    
    
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
        
    def get_database_path(self) -> Path:
        return self._db_path