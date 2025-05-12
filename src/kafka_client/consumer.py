import os
import json
from kafka import KafkaConsumer

class KafkaConsumerWrapper:
    def __init__(self, callback):
        self.topic = os.getenv("KAFKA_TOPIC", "model-results")
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
        self.callback = callback
    
    def start_consuming(self):
        for message in self.consumer:
            self.callback(message.value)