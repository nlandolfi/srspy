# simple logging for experiment runs; see tests/*.py for examples
from typing import Any, IO, List, Protocol, Tuple
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
    def open(
        self, path: str, mode: str = "wb", encoding: str = "utf-8"
    ) -> IO[bytes]: ...


# A type-hint interface for a file.
class File(Protocol):
    def write(self, b: bytes): ...

    def flush(self): ...

    def close(self): ...


# An implementation of `FS` for the local file system.
class LocalFS(object):
    @staticmethod
    def open(path: str, mode: str = "wb", encoding: str = "utf-8"):
        return open(path, mode)


class RunTrace(object):
    """
    RunTrace is a class for logging information about an experiment.
    """

    _fs: FS
    closed: bool = False
    name: str
    log_file_path: str
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
            raise ValueError("RunTrace.init: must provide keyword argument `name`")
        self.name = name

        if log_dir == "":
            log_dir = DEFAULT_LOG_DIR
        self.log_dir = log_dir

        self.log_file_path = os.path.join(self.log_dir, f"{name}_{now_str()}.json")

        self.verbose = verbose
        if verbose:
            print(f"RunTrace.init at path: {self.log_file_path}")

        self._fs = fs
        self.log_file = self._fs.open(self.log_file_path, "wb", encoding="utf-8")
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

        if summary != "" or data != {}:
            self.log(summary=summary, data=data)

        self.log_file.flush()

    def close(self, summary: str = "", data: dict = {}):
        if self.closed:
            raise Exception("RunTrace.close: called on closed log")

        if summary != "" or data != {}:
            self.log(summary=summary, data=data, type=LogEntryClose)

        self.log_file.flush()
        self.log_file.close()
        self.closed = True


class RunTraceLog(object):
    """
    'RunTraceLog' is a helper class for loading into memory an entire 'RunTrace'
    log which has *already* been written.
    """

    path: str
    entries: List[LogEntry]

    def __init__(self, path: str, fs: FS = LocalFS):
        self.path = path
        self.entries = []

        with fs.open(self.path, mode="r", encoding="utf-8") as file:
            for line in file:
                j = json.loads(line)
                self.entries.append(LogEntry.from_json(j))

    def metric(self, name: str) -> Tuple[List[Any], List[datetime.datetime]]:
        """
        Get a metric list and corresponding timestamps.

        Looks over all entries, including the first. If an entry has the 'name'
        in its 'data', then the value associated with 'name' and the 'time'
        associated with the entry are appended to lists returned to the caller.
        """
        out = []
        times = []
        for entry in self.entries:
            if name in entry.data:
                out.append(entry.data[name])
                times.append(entry.time)
        return out, times
