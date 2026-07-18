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

    def add_entry(self, entry: AbstractModel) -> Dict[str, Any]:
        """Add a new entry to the database."""
        db_response = self.read_file_data()
        if db_response.error != SUCCESS:
            return {}  # Return None if reading the database failed

        files_infos = db_response.files_infos
        files_metadata = files_infos.get("files_metadata", {})
        latest_index = files_infos.get("latest_index", 0)

        # Increment the latest index and assign it to the new entry
        latest_index += 1
        entry["id"] = latest_index
        files_metadata[str(latest_index)] = entry

        # Update the files_infos dictionary
        files_infos["latest_index"] = latest_index
        files_infos["files_metadata"] = files_metadata

        # Write the updated data back to the database
        write_response = self.write_file_data(files_infos)
        if write_response.error != SUCCESS:
            return None  # Return None if writing to the database failed

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