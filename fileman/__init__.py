"""Top-level package for RP fileman."""
# fileman/__init__.py

__app__name__ = "fileman"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    DEST_DIR_ERROR,
) = range(8)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "fileman id error",
    JSON_ERROR: "json decode error",
    DEST_DIR_ERROR: "destination directory error",
}