"""This module provides the RP fileman CLI."""
# rptodo/cli.py

import os
from pathlib import Path
from typing import Optional

import typer

from typing import List, Optional


from fileman import (ERRORS, __app__name__, __version__, config, database, fileman, filehandler)

app = typer.Typer()
DEFAULT_DEST_FOLDER_PATH = Path(os.path.expanduser("~/fileman"))


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="fileman database location?",
        help="Path to the fileman database file.",
    ),
    
    dest_path: str = typer.Option(
        str(DEFAULT_DEST_FOLDER_PATH),
        "--dest-path",
        "-dst",
        prompt="Destination folder location?",
        help="Path to the estination folder.",
    ),
) -> None:
    """Initialize the fileman database."""
    app_init_error = config.init_app(db_path, dest_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    dest_init_error = filehandler.init_dest_dir(Path(dest_path))
    if dest_init_error:
        typer.secho(
            f'Creating destination directory failed with "{ERRORS[dest_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    else:
        typer.secho(f"The fileman database is {db_path}", fg=typer.colors.GREEN)
        typer.secho(f"The destination folder is {dest_path}", fg=typer.colors.BLUE)
            

def get_file_manager() -> fileman.FileManager:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "fileman init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return fileman.FileManager(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "fileman init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app__name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return