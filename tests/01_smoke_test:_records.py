import datetime
import uuid

from srspy import records

print("THIS IS SMOKE TEST 1: IT TESTS records.py")

# Test zero types
assert records.ZeroTime
assert records.ZeroUUID

# Test LogEntryType enum
assert records.LogEntryUnknown != records.LogEntryLog
assert records.LogEntryLog != records.LogEntryClose
assert records.LogEntryClose != records.LogEntryUnknown

# Test LogEntry

## Test an empty one basics...
entry = records.LogEntry()
assert entry.type == records.LogEntryUnknown
assert entry.time == records.ZeroTime
assert entry.uuid == records.ZeroUUID
assert entry.summary == ""
assert entry.data == {}

json_dict = {
    "Type": "",
    "Time": "0001-01-01T00:00:00+00:00",
    "UUID": "00000000-0000-0000-0000-000000000000",
    "Summary": "",
    "Data": "{}",
}

assert entry.to_json() == json_dict

d = {}
entry.marshal_json(d)
assert d == json_dict

x = records.LogEntry()
x.unmarshal_json(json_dict)
assert x == entry

y = records.LogEntry.from_json(json_dict)
assert y == entry

## Try one with some fake data

entry = records.LogEntry(
    type=records.LogEntryLog,
    time=datetime.datetime(2023, 1, 1, 3, 3, tzinfo=datetime.timezone.utc),
    uuid=uuid.UUID("47d84f08-eac2-42b1-9569-740c88f4069a"),
    summary="This is a summary! \n with new lines",
    data={
        "here is": "some data",
        "and that": {
            "is neat": 123,
        },
    },
)

json_dict = {
    "Type": "log",
    "Time": "2023-01-01T03:03:00+00:00",
    "UUID": "47d84f08-eac2-42b1-9569-740c88f4069a",
    "Summary": "This is a summary! \n with new lines",
    "Data": '{"here is": "some data", "and that": {"is neat": 123}}',
}

assert entry.to_json() == json_dict

loaded = records.LogEntry.from_json(json_dict)
assert loaded == entry
