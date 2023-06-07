# simple logging for experiment runs; see tests/*.py for examples
from typing import Any
import dataclasses
import datetime
import json
import os
import uuid as uuidpkg

from dateutil.parser import isoparse

# ZeroTime is the zero time used by default for spin types.
ZeroTime = datetime.datetime(1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)

ZeroUUID = uuidpkg.UUID(int=0)

LogEntryType = str

LogEntryUnknown = ""
LogEntryLog = "log"
LogEntryClose = "close"


# simple dataclass in the style of spinpy
@dataclasses.dataclass
class LogEntry:
    type: LogEntryType = LogEntryUnknown
    time: datetime.datetime = ZeroTime
    uuid: uuidpkg.UUID = ZeroUUID
    summary: str = ""
    data: dict = dataclasses.field(default_factory=dict)  # json, why not

    @staticmethod
    def from_json(j: dict):
        return LogEntry().unmarshal_json(j)

    def unmarshal_json(self, j: dict):
        if "Type" in j:
            self.type = LogEntryType(j["Type"])
        if "Time" in j:
            self.time = isoparse(j["Time"])
        if "UUID" in j:
            self.uuid = uuidpkg.UUID(j["UUID"])
        if "Summary" in j:
            self.summary = j["Summary"]
        if "Data" in j:
            self.data = json.loads(j["Data"])

    def to_json(self):
        j = {}
        self.marshal_json(j)
        return j

    def marshal_json(self, j: dict):
        j["Type"] = self.type
        j["Time"] = self.time.isoformat()
        j["UUID"] = str(self.uuid)
        j["Summary"] = self.summary
        j["Data"] = json.dumps(self.data)


# default dir to use; override via RunTrace(..., log_dir=<here>, ...)
LOG_DIR = "../runs/"


# get the time as a string that we can use as a path (no spaces)
def now_str():
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
    log_file: Any  # file

    def __init__(self, name=None, data={}, log_dir=None, fs=None, verbose=False):
        if name is None:
            raise ValueError("RunTrace.init: name must be set")
        self.name = self

        # log directory
        if log_dir is None:
            log_dir = LOG_DIR
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

    def log(self, summary="", data={}, type=LogEntryLog):
        if self.closed:
            raise Exception("RunTrace.log: called on closed log")

        s = json.dumps(
            LogEntry(
                type=type,
                time=datetime.datetime.now(),
                uuid=uuidpkg.uuid4(),
                summary=summary,
                data=data,
            ).to_json(),
        )
        self.log_file.write(bytes(s, "utf-8"))
        self.log_file.write(b"\n")

    def flush(self, summary="", data={}):
        if self.closed:
            raise Exception("RunTrace.flush: called on closed log")

        self.log(summary=summary, data=data)
        self.log_file.flush()

    def close(self, summary="", data={}):
        if self.closed:
            raise Exception("RunTrace.close: called on closed log")

        self.log(summary=summary, data=data, type=LogEntryClose)
        self.log_file.flush()
        self.log_file.close()
        self.closed = True
