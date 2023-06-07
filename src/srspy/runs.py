# simple logging for experiment runs; see tests/*.py for examples
from typing import IO
import datetime
import json
import os
import uuid


from .records import LogEntry, LogEntryType, LogEntryLog, LogEntryClose

# default dir to use; override via RunTrace(..., log_dir=<here>, ...)
DEFAULT_LOG_DIR: str = "../runs/"


def now_str():
    """
    A helper function to get the current time as a string that
    we can use as a path (e.g., it has no spaces).

    This function is a helper to `RunTrace.__init__` below

    """
    return str(datetime.datetime.now()).replace(" ", "_")


# load a log which has _already_ been written
class RunTraceLog(object):
    def __init__(self, path):
        self.path = path
        self.entries = []

        with open(self.path, "r") as file:
            for line in file:
                j = json.loads(line)
                self.entries.append(LogEntry.from_json(j))

    def metric(self, name: str):
        out = []
        for entry in self.entries:
            if name in entry.data:
                out.append(entry.data[name])
        return out


class RunTrace(object):
    closed: bool = False
    name: str
    log_file: IO[bytes]  # e.g. local file, file-like, spin file

    def __init__(
        self,
        name: str = "",
        log_dir: str = "",
        data: dict = {},
        fs=None,
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

        if fs is None:
            o = open
        else:
            o = fs.open

        self.log_file = o(self.log_file_path, "wb")

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
