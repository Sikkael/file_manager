"""This module provides the database functionality."""
# fileman/database.py

import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from fileman import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS


DEFAULT_DB_FILE_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_fileman.json"
)


        


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """Create the database."""
    __dict__ = { "directories": [],  "files_stats": {}, "files_metadata": {} }
    try:
        with db_path.open("w") as db:
           json.dump(__dict__, db, indent=4)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR
    
class DBResponse(NamedTuple):
    file_infos: Dict[str, Any]
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

    def write_file_data(self, file_infos: Dict[str,Any]) -> DBResponse:
        try:
            with self._db_path.open("w") as db:
                json.dump(file_infos, db, indent=4)
            return DBResponse(file_infos, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(file_infos, DB_WRITE_ERROR)