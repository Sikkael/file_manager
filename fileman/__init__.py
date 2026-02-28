"""Top-level package for RP fileman."""
# fileman/__init__.py

__app__name__ = "fileman"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_NOT_FOUND_ERROR,
    FILE_ERROR,
    CONFIG_DIR_ERROR,
    CONFIG_FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    DIR_EXIST_ERROR,
    DEST_DIR_ERROR,
    DIR_ALREADY_ADDED_ERROR,
    METADATA_ERROR,
) = range(13)

ERRORS = {
    DIR_NOT_FOUND_ERROR: "directory not found error",
    FILE_ERROR: "file error",
    CONFIG_DIR_ERROR: "config directory error",
    CONFIG_FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "fileman id error",
    JSON_ERROR: "json decode error",
    DIR_EXIST_ERROR: "destination directory already exist error",
    DIR_ALREADY_ADDED_ERROR: "directory already added error",
    DEST_DIR_ERROR: "destination directory error",
    METADATA_ERROR: "metadata error"
}

(NEW, MOVED, DUPLICATE, ERROR) = range(4)



FILE_STATUS = {
    NEW: "new file",
    MOVED: "moved file",
    DUPLICATE: "duplicate file",
    ERROR: "file error"
}