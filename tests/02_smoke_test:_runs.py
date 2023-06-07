import pytest
import io
from typing import IO

from srspy import runs

print("THIS IS SMOKE TEST 2: IT TESTS basics")

# Sundry basic tests
assert runs.DEFAULT_LOG_DIR

assert runs.now_str()
assert " " not in runs.now_str()  # doesn't have spaces

assert runs.File
assert runs.FS
assert runs.LocalFS
assert runs.LocalFS.open("/dev/null")  # basic open


# Some stubs for the file system stuff.
class StubFile(object):
    mode: str
    closed: bool = False
    flushed: bool = True
    buffer: IO

    def __init__(self, mode: str):
        if "w" not in mode:
            raise ValueError("StubFile: mode not writable")

        self.mode = mode
        self.buffer = io.BytesIO()

    def write(self, bs: bytes):
        if self.closed:
            raise Exception("StubFile: write on closed file")

        self.buffer.write(bs)
        self.Flushed = False

    def flush(self):
        # no op
        self.flushed = True

    def close(self):
        self.closed = True


with pytest.raises(ValueError):
    StubFile("asdf")  # mode does not have w

with pytest.raises(Exception):
    f = StubFile("wb")
    assert f.closed
    f.write()  # file closed

assert StubFile("wb").flushed

f = StubFile("wb")
f.write(b"asdf")


class StubFS(object):
    files: dict

    def __init__(self):
        self.files = {}

    def open(self, path, mode):
        file = StubFile(mode)
        self.files[path] = file
        return file


fs = StubFS()
assert len(f.files) == 0
f.open("one", "wb")
f.open("two", "wb")
assert len(f.files) == 2


with pytest.raises(ValueError):
    runs.RunTrace()  # lacks name

## Use the stubbed file system
fs = StubFS()
r = runs.RunTrace(name="test", fs=fs)
r.log(summary="this is a test", data={"metric": 100})
r.flush(summary="this will flush right after the write", data={"metric": 101})
r.close()

assert len(fs.files) == 1
fname = list(fs.files.keys())[0]
assert " " not in fname
file = fs.files[fname]
assert file.flushed
assert file.closed
# example value (we don't compare on this because the times and UUIDs change)
#  b'{"Type": "log", "Time": "2023-06-07T14:44:08.774714", "UUID": "bd998f0b-04c8-479a-a480-8b0a2f451897", "Summary": "test 2023-06-07_14:44:08.774712", "DataJSON": "{}"}\n{"Type": "log", "Time": "2023-06-07T14:44:08.774745", "UUID": "60af77d8-f024-4988-aa50-36699360be2b", "Summary": "this is a test", "DataJSON": "{\\"metric\\": 100}"}\n{"Type": "log", "Time": "2023-06-07T14:44:08.774757", "UUID": "8e91476d-9828-482e-8295-dd90b3626737", "Summary": "this will flush write after the write", "DataJSON": "{\\"metric\\": 101}"}\n{"Type": "close", "Time": "2023-06-07T14:44:08.774769", "UUID": "f35bbb42-5151-44a2-bb86-56d7d0b7a961", "Summary": "", "DataJSON": "{}"}\n'  # noqa: E501
val = str(file.buffer.getvalue())
assert "test" in val
assert "this is a test" in val
assert "this will flush right after" in val
assert "metric" in val

## Use the actual local file system
r = runs.RunTrace(name="test", log_dir="/tmp")
r.log(summary="this is a test", data={"metric": 100})
r.flush(summary="this will flush right after the write", data={"metric": 101})
r.close()
