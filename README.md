[![Build Status](https://travis-ci.org/huangxiaohen2738/flask-kafka.svg?branch=master)](https://travis-ci.org/huangxiaohen2738/flask-kafka)


## How to Use
#### Create

```python
from flask_kafka import KafkaQueue

kqueue = KafkaQueue("name")
```

#### Init

```python
kqueue.init_app(app)
topic = kqueue.subscribe("test-topic", {"avro": "schema"})


@topic.connect
def do_something(sender, record):
   pass
```
