srspy
-----

A package for simple research experiment tracing. Python 3.

```bash
pip install srspy
```

For example,
```python
from srspy import RunTrace

# ...

r = RunTrace(name="train_model", data={
    "epochs": epochs,
    "batch_size": batch_size,
    "p": p,
    "λ": lamb,
    "optimizer": "adam",
    "lr": 0.0001,
    "gpu": GPU,
    "bias": bias,
}, log_dir="./runs")

# ...

for epoch in ...:
    # ...
    r.flush(data={"epoch_loss": epoch_loss})

# ...
r.close()

# later
l = RunTraceLog(r.log_file_path)
losses, timestamps = l.metric("epoch_loss")
```
