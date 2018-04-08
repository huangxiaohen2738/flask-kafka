import logging
import os

from blinker import Namespace
from collections import OrderedDict
from fastavro import schemaless_reader
from io import BytesIO
from kafka import KafkaConsumer
from kafka.structs import TopicPartition


logger = logging.getLogger(__name__)


class KafkaQueue(object):
    TOPICS = OrderedDict()

    def __init__(self, name, lag_sampling_percent=1, group_id=None):
        self.name = name
        self.group_id = name.lower() if not group_id else group_id	
        self.signal = Namespace()
        self.servers = None
        self.multiples = []
        self.cnt = 0
        self.instance_idx = int(os.environ.get("DEPLOYD_POD_INSTANCE_NO", 0))

    def init_app(self, app):
        self.servers = app.config["KAFKA_SERVERS"]
        self.workers = app.config["KAFKA_WORKERS"]

    def get_signal(self, topic):
        return self.signal.signal(topic)

    def subscribe(self, topic, schema, multiples=False):
        self.TOPICS[topic] = schema
        return self.get_signal(topic)

    def get_topics(self):
        topics = list(self.TOPICS.keys())
        idx = self.instance_idx - 1
        if idx < 0:
            return topics
        slice_size = int(float(len(topics)) / self.workers + 0.5)

        start = idx * slice_size
        end = start + slice_size
        logger.info(
            "woker idx is[%s], topics(%d) from: [%d:%d]"
            % (idx, len(topics), start, end)
        )
        return topics[start:end]

    def log_lag(self, consumer, msg):
        self.cnt += 1
        if self.cnt == 100:
            topic = msg.topic
            partition = msg.partition
            highwater = consumer.highwater(TopicPartition(topic, partition))
            lag = highwater - 1 - msg.offset
            logger.info("lag <%s@%s>: %s" % (topic, partition, lag))
            self.cnt == 0

    def start_consume(self):
        logger.info("start to consume kafka %s messages!" % (self.name,))
        topics = self.get_topics()
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.servers,
            group_id=self.group_id
        )
        for msg in consumer:
            self.log_lag(consumer, msg)
            topic = msg.topic
            schema = self.TOPICS[topic]
            record = schemaless_reader(BytesIO(msg.value[5:]), schema)
            self.get_signal(topic).send(self, record=record)
