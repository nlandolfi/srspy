import dataclasses
import datetime
import json
import uuid as uuidpkg  # to avoid conflict with uuid type annotation below

from dateutil.parser import isoparse

# ZeroTime is the zero time used for datetime.datetime types.
ZeroTime: datetime.datetime = datetime.datetime(
    1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
)

# ZeroUUID is the zero UUID used for UUID types.
ZeroUUID: uuidpkg.UUID = uuidpkg.UUID(int=0)

# A helper enum type; see values below.
LogEntryType = str

# Various values for LogEntryType
LogEntryUnknown: LogEntryType = ""
LogEntryLog: LogEntryType = "log"
LogEntryClose: LogEntryType = "close"


# simple dataclass in the style of spinpy
@dataclasses.dataclass
class LogEntry:
    type: LogEntryType = LogEntryUnknown
    time: datetime.datetime = ZeroTime
    uuid: uuidpkg.UUID = ZeroUUID
    summary: str = ""
    data: dict = dataclasses.field(default_factory=dict)  # json, why not

    @staticmethod
    def from_json(j: dict) -> "LogEntry":
        entry = LogEntry()
        entry.unmarshal_json(j)
        return entry

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

    def to_json(self) -> dict:
        j: dict = {}
        self.marshal_json(j)
        return j

    def marshal_json(self, j: dict):
        j["Type"] = self.type
        j["Time"] = self.time.isoformat()
        j["UUID"] = str(self.uuid)
        j["Summary"] = self.summary
        j["Data"] = json.dumps(self.data)
