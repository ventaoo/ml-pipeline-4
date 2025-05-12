import configparser
import os
import sys
import json
import joblib
from datetime import datetime
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from gensim.models import Word2Vec
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka import KafkaConsumer
from threading import Thread
from contextlib import asynccontextmanager

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from db import store_prediction_results
from init_env import decrypt_with_ansible_lib

encrypted_file = os.getenv("DECRYPT_FILE_PATH")
encrypted_password = os.getenv("DECRYPT_PASSWORD")
output_file = os.getenv("OUTPUT_FILE")
decrypt_with_ansible_lib(encrypted_file, encrypted_password, output_file)


# 定义 Consumer 后台任务
def consume_messages():
    consumer = KafkaConsumer(
        "model-results", # TODO 需要从参数获取
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        auto_offset_reset="earliest",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )
    for message in consumer:
        print(f"Consumer 收到消息: {message.value}")
        # 在此处添加业务逻辑（如保存到数据库）

# 定义数据输入格式
class InputData(BaseModel):
    text: str

# API 类
class api_():
    def __init__(self):
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # 加载模型
        self.model = joblib.load(self.config['LOG_REG']['path'])
        self.word2vec_model = Word2Vec.load(self.config['WORD2VEC']['model_path'])

    def text_to_vector(self, model, text):
        """ 将文本转换为词向量的平均值 """
        words = text.split()
        vectors = [model.wv[word] for word in words if word in model.wv]
        return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

    def predict(self, input_text):
        """ 执行预测 """
        input_data = np.array([self.text_to_vector(self.word2vec_model, input_text)])
        prediction = self.model.predict(input_data)
        return int(prediction)  # 确保返回整数

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 服务器启动!")
     # 从环境变量读取 Kafka 配置（示例值：kafka:9092）
    app.kafka_producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    print('Kafka producer 启动!')

    # 启动 Consumer 线程
    # TODO 单独consumer类
    Thread(target=consume_messages, daemon=True).start()
    print('Kafka consumer 启动!')

    yield
    
    app.kafka_producer.close()
    print("🛑 服务器关闭!")

# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# 预测 API 实例
api_interface = api_()

# 预测接口
@app.get("/predict/{data}")
def predict(data: str):
    prediction = api_interface.predict(data)
    
    # 存入数据库时存储 (输入文本, 预测结果)
    store_prediction_results([(data, prediction)], "predictions")  

    # 发送消息到 Kafka
    message = {
        "input": data,
        "prediction": prediction,
        "timestamp": datetime.now().isoformat()
    }
    app.kafka_producer.send("model-results", value=message)
    
    return {"input": data, "prediction": prediction}
