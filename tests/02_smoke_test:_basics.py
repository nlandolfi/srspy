from srspy import srs

print("THIS IS SMOKE TEST 1: IT TESTS basics")

r = srs.RunTrace(name="test", log_dir="/tmp")
r.log(summary="this is a test", data={"metric": 100})
r.flush(summary="this will flush write after the write", data={"metric": 101})
r.close()
