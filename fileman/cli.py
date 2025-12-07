"""This module provides the RP fileman CLI."""
# rptodo/cli.py

import configparser
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
            
@app.command()
def add(
         dirname: str = typer.Option( 
        "--dirname", 
        "-dir"),
         not_found_ok:bool = typer.Option(
        False,
        "--not-found-ok",
        "-nfo",
        help="If the directory does not exist, do not raise an error.",
    ),
      )-> None:
    """Add a new directory to the database."""
    file_manager = get_file_manager()
    current_directory = file_manager.add(dirname, not_found_ok)
    if current_directory.error:
        typer.secho(
            f'Adding directory failed with "{ERRORS[current_directory.error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f'Directory "{dirname}" added successfully.',
            fg=typer.colors.GREEN,
        )

def get_file_manager() -> fileman.FileManager:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
        dest_path = filehandler.get_dest_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "fileman init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return fileman.FileManager(db_path,dest_path)
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

@app.command(name="list")
def list_all() -> None:
    """List directories"""
    file_manager = get_file_manager()
    dir_list = file_manager.get_dir_list()
    if len(dir_list) == 0:
        typer.secho(
            "There are no dir list yet", fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\ndir list:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.  ",
        "| Directory Name |",
     
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers)+ "\n", fg=typer.colors.BLUE)
    id = -1
    for dirname in dir_list:
        id+=1
        typer.secho(
            f"{id+1}. | {dirname} |",
            fg=typer.colors.BLUE,
            bold=True
        )
        typer.secho("\n"+"-" * len(headers) + "\n", fg=typer.colors.BLUE)