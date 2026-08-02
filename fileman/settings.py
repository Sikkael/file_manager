import configparser
from pathlib import Path

import typer

from fileman import (
    CONFIG_FILE_ERROR, DB_WRITE_ERROR, DEST_DIR_ERROR, DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, FILE_ERROR, SUCCESS, __app__name__
)


class Settings:
    """Application settings class, holds all app settings.
    """
    
    database_connection_str: str = ""
    class Config:
        pass