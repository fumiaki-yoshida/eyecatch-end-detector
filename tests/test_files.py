from src.file import get_files
from pathlib import Path
from pytest import fixture


@fixture
def mock_files():
    files = [
        Path("files/file1.webm"),
        Path("files/file2.mp4"),
        Path("files/file3.avi"),
        Path("files/subdir/file4.mkv"),
        Path("files/subdir/file5.mov"), 
        Path("files/subdir/file6.txt"),
        Path("files/subdir/file7.jpg"),
        Path("files/subdir/file8.csv"),
    ]


def test_get_files(mock_files):
    files = get_files("files")
    assert isinstance(files, list)
    assert all(isinstance(file, str) for file in files)
