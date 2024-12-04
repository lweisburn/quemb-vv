import os
from pathlib import Path
from tempfile import mkdtemp

from pytest import raises

from quemb.shared.manage_scratch import WorkDir


def test_already_created():
    my_tmp = Path(mkdtemp())
    assert my_tmp.exists()

    scratch = WorkDir(my_tmp)

    scratch.cleanup()
    assert not my_tmp.exists()

    with raises(FileNotFoundError):
        scratch.cleanup()


def test_keep_upon_error():
    my_tmp = Path(mkdtemp())
    assert my_tmp.exists()

    with raises(ValueError):
        with WorkDir(my_tmp):
            raise ValueError
    assert my_tmp.exists()

    with WorkDir(my_tmp):
        pass
    assert not my_tmp.exists()


def test_already_created_non_empty():
    my_tmp = Path(mkdtemp())

    assert my_tmp.exists()

    testfile = my_tmp / "testfile"
    testfile.touch()
    with raises(ValueError):
        with WorkDir(my_tmp):
            pass

    assert my_tmp.exists()


def test_context_manager():
    my_tmp = Path(mkdtemp())
    assert my_tmp.exists()

    with WorkDir(my_tmp):
        pass

    assert not my_tmp.exists()


def test_creation_user_defined():
    test_dir = Path("./scratch_test")
    with WorkDir("./scratch_test") as scratch:
        assert test_dir.exists()
        assert scratch.path == test_dir.resolve()
    assert not test_dir.exists()


def test_creation_PID():
    PID = os.getpid()
    with WorkDir(scratch_area=Path("./scratch_root")) as scratch_root:
        tmp_root = scratch_root.path
        with WorkDir.from_environment(user_defined_root=tmp_root) as dir:
            assert dir.path == tmp_root / f"QuEmb_{PID}"
            with WorkDir.from_environment(user_defined_root=tmp_root) as dir_2:
                assert dir_2.path == tmp_root / f"QuEmb_{PID + 1}"


def test_dunder_methods():
    "Test if we can use an instance of `WorkDir` as if it was a `Path`"
    with WorkDir(scratch_area=Path("./scratch")) as scratch:
        with open(scratch / "test.txt", "w") as f:
            f.write("hello world")

        with open(scratch.path / "test.txt") as f:
            assert f.read() == "hello world"
