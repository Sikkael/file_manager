

import configparser
from pathlib import Path

from fileman import DB_WRITE_ERROR, DEST_DIR_ERROR, SUCCESS


def init_dest_dir(dest_path: Path) -> int:
    """Create the database."""
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
        return SUCCESS
    except OSError:
        return DEST_DIR_ERROR
    
def get_dest_path(config_file: Path) -> Path:
    """Return the current path to the database."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["destination directory"])
