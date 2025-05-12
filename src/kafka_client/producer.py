import os
import json
from kafka import KafkaProducer

class KafkaProducerWrapper:
    def __init__(self):
        self.topic = os.getenv("KAFKA_TOPIC", "model-results")
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    
    def send_message(self, message):
        self.producer.send(self.topic, value=message)