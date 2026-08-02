"""This module provides the database functionality."""
# fileman/database.py

import configparser
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS
from fileman.models import BaseModel


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])


class DBResponse(NamedTuple):
    data: Dict[Any, Any]
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
        self.load_database()  # Load the database upon initialization
        
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

    def add_entry(self, entry: BaseModel) -> BaseModel:
        """Add a new entry to the database."""
        _data_ = self._data_.get(entry.__class__.__name__, {})
        
        if entry.id not in _data_:
           entry.id = max(_data_.keys(), default=0) + 1  # Assign a new ID
        
        _data_[entry.id] = entry.to_dict()  # Store the entry as a dictionary
        self._data_[entry.__class__.__name__] = _data_  
        return entry  # Return the newly added entry with its ID    
    
    def save(self) -> int:
        """Save the current state of the database to the JSON file."""
        try:
            with self._db_path.open("w") as db:
                json.dump(self._data_, db, indent=4)
            return SUCCESS
        except OSError:  # Catch file IO problems
            return DB_WRITE_ERROR
    
    def select(self, model_cls: type, id: int) -> DBResponse:
        """Select entries of a specific model class from the database."""
        if model_cls.__name__ not in self._data_ or id not in self._data_[model_cls.__name__]:
            return DBResponse({}, DB_READ_ERROR)  # Return empty if no entries exist for the model class
        return DBResponse(self._data_.get(model_cls.__name__, {}).get(id, {}), SUCCESS)
        
    def select_all(self, model_cls: type, filter_func=None) -> DBResponse:
        """Select all entries of a specific model class from the database."""
        if model_cls.__name__ not in self._data_:
            return DBResponse({}, DB_READ_ERROR)  # Return empty if no entries exist for the model class
        entries = self._data_[model_cls.__name__]
        if filter_func:
            entries = {k: v for k, v in entries.items() if filter_func(v)}
        return DBResponse(entries, SUCCESS)
    
    def delete_entry(self, model_cls: type, id: int) -> int:
        """Delete an entry of a specific model class from the database."""
        if model_cls.__name__ not in self._data_ or id not in self._data_[model_cls.__name__]:
            return DB_READ_ERROR  # Return error if entry does not exist
        del self._data_[model_cls.__name__][id]
        return SUCCESS  # Return success after deletion

    def copy_database(self) -> int:
        try:
            shutil.copy2(self._db_path, Path.cwd())
            return SUCCESS
        except OSError:  # Catch file IO problems
            return DB_READ_ERROR
        
    def get_database_path(self) -> Path:
        return self._db_path
    
    