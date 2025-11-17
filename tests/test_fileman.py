# tests/test_fileman.py

from typer.testing import CliRunner

from fileman import __app__name__, __version__, cli

import json

import pytest
from typer.testing import CliRunner

from fileman import (
    DB_READ_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    rptodo,
)


runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app__name__} v{__version__}\n" in result.stdout
    
@pytest.fixture
def mock_json_file(tmp_path):
    fileman = [{"Description": "", "filename": "myfilename"}]
    db_file = tmp_path / "fileman.json"
    with db_file.open("w") as db:
        json.dump(fileman, db, indent=4)
    return db_file

# tests/test_fileman.py
# ...

test_data1 = {
   
}
test_data2 = {
   
}


"""@pytest.mark.parametrize(
    "description, priority, expected",
    [
        pytest.param(
            test_data1["description"],
            test_data1["priority"],
            (test_data1["todo"], SUCCESS),
        ),
        pytest.param(
            test_data2["description"],
            test_data2["priority"],
            (test_data2["todo"], SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, description, priority, expected):
    todoer = rptodo.Todoer(mock_json_file)
    assert todoer.add(description, priority) == expected
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 2"""