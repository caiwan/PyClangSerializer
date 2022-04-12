import pytest
import os
import clang.cindex as clang_index


@pytest.fixture(scope="session")
def clang_path():
    return os.getenv("CLANG_PATH")


@pytest.fixture(scope="session")
def clang_index_parser(clang_path) -> clang_index.Index:
    clang_index.Config.set_library_path(clang_path)
    return clang_index.Index.create()
