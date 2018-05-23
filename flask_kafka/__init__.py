import logging
import json
import os

from blinker import Namespace
from confluent_kafka import avro, KafkaError
from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from .utils import slicer


logger = logging.getLogger(__name__)


class KafkaQueue(object):
    TOPICS = []

    def __init__(self, name):
        self.name = name
        self.signal = Namespace()
        self.instance_idx = int(os.environ.get("DEPLOYD_POD_INSTANCE_NO", 0))
        self.partition_map = None

    def init_app(self, app):
        self.config = {
            "bootstrap.servers": ",".join(app.config["KAFKA_SERVERS"]),
            "group.id": self.name.lower(),
            "schema.registry.url": app.config["KAFKA_SCHEMA_REGISTRY"]
        }
        self.partition_map = app.config["KAFKA_PARTITION_MAP"]
        self.workers = app.config["KAFKA_WORKERS"]

    def get_signal(self, topic):
        return self.signal.signal(topic)

    def subscribe(self, topic):
        self.TOPICS.append(topic)
        return self.get_signal(topic)

    def get_topics(self):
        topics = []
        for topic in self.TOPICS:
            topics += [topic] * self.partition_map.get(topic, 1)
        idx = self.instance_idx - 1
        if idx < 0:
            return topics
        target = slicer(topics, self.workers)[idx]
        logger.info(
            "woker idx is[%s], topics(%d) from: %s"
            % (idx, len(topics), target)
        )
        return target

    def start_consume(self):
        logger.info("start to consume kafka %s messages!" % (self.name,))
        topics = list(set(self.get_topics()))

        consumer = AvroConsumer(self.config)
        consumer.subscribe(topics)

        while True:
            try:
                msg = consumer.poll()
            except SerializerError:
                logger.critical("deserialization failed", exc_info=True)
                break
            if msg is None:
                logger.debug("message timeout")
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug("partition eof")
                    continue
                else:
                    logger.critical("encounter error: %s", msg.error())
                    break
            topic = msg.topic()
            self.get_signal(topic).send(self, record=msg.value())


class KafkaProducer(object):
    def __init__(self):
        self.producer = None
        self._max_retries = 3
        self.topics = {}

    def register_topic(self, topic, schema):
        self.topics[topic] = avro.loads(json.dumps(schema))

    def init_app(self, app):
        bootstrap_servers = ",".join(app.config["KAFKA_SERVERS"])
        schema_registry = app.config["KAFKA_SCHEMA_REGISTRY"]

        self.producer = AvroProducer({
            "bootstrap.servers": bootstrap_servers,
            "schema.registry.url": schema_registry
        })

    def produce(self, topic, value):
        schema = self.topics.get(topic)
        if schema is None:
            raise ValueError("register [{0}] with schema first".format(topic))
        for __ in xrange(self._max_retries):
            try:
                self.producer.produce(
                    topic=topic, value=value, value_schema=schema)
                break
            except BufferError:
                self.producer.poll(0.1)
                continue
