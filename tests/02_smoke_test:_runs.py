from srspy import RunTrace

print("THIS IS SMOKE TEST 2: IT TESTS basics")

r = RunTrace(name="test", log_dir="/tmp")
r.log(summary="this is a test", data={"metric": 100})
r.flush(summary="this will flush write after the write", data={"metric": 101})
r.close()
