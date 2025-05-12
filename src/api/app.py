import configparser
import os
import sys
import joblib
from datetime import datetime
import numpy as np
from fastapi import FastAPI
from gensim.models import Word2Vec
from threading import Thread
from contextlib import asynccontextmanager

sys.path.insert(1, os.path.join(os.getcwd(), "src"))
from kafka_client.producer import KafkaProducerWrapper
from kafka_client.consumer import KafkaConsumerWrapper

from db import store_prediction_results
from init_env import decrypt_with_ansible_lib

encrypted_file = os.getenv("DECRYPT_FILE_PATH")
encrypted_password = os.getenv("DECRYPT_PASSWORD")
output_file = os.getenv("OUTPUT_FILE")
decrypt_with_ansible_lib(encrypted_file, encrypted_password, output_file)

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

# 定义Consumer回调函数
def message_callback(message):
    print(f"Consumer 收到消息: {message}")
    store_prediction_results([(message["input"], message["prediction"])], "predictions")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 服务器启动!")
    
    # 初始化Producer
    app.kafka_producer = KafkaProducerWrapper()
    print('Kafka producer 启动!')

    # 启动Consumer线程
    consumer = KafkaConsumerWrapper(message_callback)
    Thread(target=consumer.start_consuming, daemon=True).start()
    print('Kafka consumer 启动!')

    yield
    
    app.kafka_producer.producer.close()
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
    app.kafka_producer.send_message(message)
    
    return {"input": data, "prediction": prediction}
