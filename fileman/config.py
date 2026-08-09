"""This module provides the RP fileman config functionality."""
# fileman/config.py

import configparser
from pathlib import Path

import typer

from fileman import (
    CONFIG_FILE_ERROR, DB_WRITE_ERROR, DEST_DIR_ERROR, DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, FILE_ERROR, SUCCESS, __app__name__
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app__name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
DEFAULT_APP_FOLDER_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_fileman"
)

DB_FILENAME = "." + Path.home().stem + "_fileman.json"


def init_app(app_folder_path: str) -> int:
    """Initialize the application."""
    config_code = _init_config_file(app_folder_path)
    if config_code != SUCCESS:
        return config_code
    
    return SUCCESS

def init_dest_dir(app_folder_path: Path) -> int:
    """Initialize the destination directory."""
    if app_folder_path.exists():
       return DIR_EXIST_ERROR
    try:
        app_folder_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR

def _init_config_file(app_folder_path: str) -> int:
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_NOT_FOUND_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
        db_path = Path(app_folder_path).joinpath(DB_FILENAME)
        # writing config file with the app folder path and database path
        config_parser = configparser.ConfigParser()
        config_parser["General"] = {"app_folder_path": app_folder_path, "database": str(db_path)}
        with CONFIG_FILE_PATH.open("w") as file:
                    config_parser.write(file) 
    except OSError:
        return CONFIG_FILE_ERROR
    return SUCCESS

def _create_ressource(app_folder_path: str) -> int:
    # creating application folder and database file
    if init_dest_dir(Path(app_folder_path)) != SUCCESS:
        return DIR_EXIST_ERROR
    # database file is created in the application folder
    db_path = Path(app_folder_path).joinpath(DB_FILENAME)
    if init_repos(db_path) != SUCCESS:
            return DB_WRITE_ERROR
    
    # writing config file with the app folder path and database path
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"app_folder_path": app_folder_path, "database": str(db_path)}
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)    
    except OSError:
        return CONFIG_FILE_ERROR
    return SUCCESS

def _create_dest_dir(dest_path: Path) -> int:
    """Initialize the destination directory."""
    dest_folfer = dest_path.joinpath(str(dest_path)+ "._fileman")
    if dest_folfer.exists():
       return DIR_EXIST_ERROR
    config_parser = configparser.ConfigParser()
    config_parser["General"]["dest_directory"]  = str(dest_folfer)                                
    try:
        Path(dest_path).mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
        return SUCCESS
    except OSError:
        return DIR_EXIST_ERROR
