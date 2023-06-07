# simple logging for experiment runs; see tests/*.py for examples
from typing import IO, Protocol
import datetime
import json
import os
import uuid

from .records import LogEntry, LogEntryType, LogEntryLog, LogEntryClose

# default dir to use; override via RunTrace(..., log_dir=<here>, ...)
DEFAULT_LOG_DIR: str = "./runs/"


def now_str():
    """
    A helper function to get the current time as a string that
    we can use as a path (e.g., it has no spaces).

    This function is a helper to `RunTrace.__init__` below
    """
    return str(datetime.datetime.now()).replace(" ", "_")


# A type-hint interface for a file system.
class FS(Protocol):
    def open(self, name: str, mode: str = "wb") -> IO[bytes]:
        ...


# A type-hint interface for File methods required.
class File(Protocol):
    def write(self, bytes):
        ...

    def flush(self):
        ...

    def close(self):
        ...


# An implementation of `FS` for the local file system.
class LocalFS(object):
    @staticmethod
    def open(name: str, mode: str = "wb"):
        return open(name, mode)


class RunTrace(object):
    """
    RunTrace is a class for logging information about an experiment.
    """

    _fs: FS
    closed: bool = False
    name: str
    log_file: File  # e.g. local file, file-like, spin file

    def __init__(
        self,
        name: str = "",
        log_dir: str = "",
        data: dict = {},
        fs: FS = LocalFS,
        verbose=False,
    ):
        if name == "":
            raise ValueError("RunTrace.init: name must be set")
        self.name = name

        if log_dir == "":
            log_dir = DEFAULT_LOG_DIR
        self.log_dir = log_dir

        self.log_file_path = os.path.join(self.log_dir, f"{name}_{now_str()}.json")

        self.verbose = verbose
        if verbose:
            print(f"RunTrace.init at path: {self.log_file_path}")

        self._fs = fs
        self.log_file = fs.open(self.log_file_path, "wb")
        self.log(summary=f"{name} {now_str()}", data=data)

    def log(self, summary: str = "", data: dict = {}, type: LogEntryType = LogEntryLog):
        if self.closed:
            raise Exception("RunTrace.log: called on closed log")

        s = json.dumps(
            LogEntry(
                type=type,
                time=datetime.datetime.now(),
                uuid=uuid.uuid4(),
                summary=summary,
                data=data,
            ).to_json(),
        )
        self.log_file.write(bytes(s, "utf-8"))
        self.log_file.write(b"\n")

    def flush(self, summary: str = "", data: dict = {}):
        if self.closed:
            raise Exception("RunTrace.flush: called on closed log")

        self.log(summary=summary, data=data)
        self.log_file.flush()

    def close(self, summary: str = "", data: dict = {}):
        if self.closed:
            raise Exception("RunTrace.close: called on closed log")

        self.log(summary=summary, data=data, type=LogEntryClose)
        self.log_file.flush()
        self.log_file.close()
        self.closed = True
