## How to install

## How to Use
#### Create

```python
from flask_kafka import KafkaQueue

kqueue = KafkaQueue("name", {"avro": "schema"})
```

#### Init

```python
kqueue.init_app()
topic = kqueue.subscribe("test-topic")


@topic.connect
def do_something(sender, record):
   pass
```
