"""This module provides the RP fileman config functionality."""
# fileman/config.py

import configparser
from pathlib import Path

import typer

from fileman import (
    DB_WRITE_ERROR, DIR_ERROR, FILE_ERROR, SUCCESS, DEST_DIR_ERROR,__app__name__
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app__name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def init_app(db_path: str, dst_path:str) -> int:
    """Initialize the application."""
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    database_code = _create_database(db_path,dst_path)
    if database_code != SUCCESS:
        return database_code
    return SUCCESS

def _init_config_file() -> int:
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR
    return SUCCESS

def _create_database(db_path: str,dest_path: str) -> int:
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"database": db_path}
    config_parser["General"] = {"destination directory": dest_path}
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return DB_WRITE_ERROR
    return SUCCESS


