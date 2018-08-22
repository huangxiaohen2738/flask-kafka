[![Build Status](https://travis-ci.org/huangxiaohen2738/flask-kafka.svg?branch=master)](https://travis-ci.org/huangxiaohen2738/flask-kafka)


## How to Use
#### Create

```python
from flask_kafka import KafkaQueue
from flask_kafka import KafkaProducer

kqueue = KafkaQueue("name")
kproducer = KafkaProducer()

```

#### Init

```python
kqueue.init_app(app)
topic = kqueue.subscribe("test-topic")

kproducer.init_app(app)

@topic.connect
def do_something(sender, record):
   pass
```


#### start

```python
kqueue.start_consume()
kproducer.produce(topic, value)
```
