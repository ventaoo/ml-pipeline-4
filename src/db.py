import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from typing import List, Tuple

# 加载环境变量
load_dotenv()

# 从环境变量中获取数据库连接信息
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

"""
DROP TABLE IF EXISTS jeopardy;


CREATE TABLE jeopardy (
    "Show Number" INTEGER,
    " Air Date" DATE,
    " Round" TEXT,
    " Category" TEXT,
    " Value" TEXT,
    " Question" TEXT,
    " Answer" TEXT
);

DROP TABLE IF EXISTS predictions;

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,        -- 自动递增的主键
    prediction_value INT NOT NULL, -- 存储预测值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 存储记录的时间戳
);
"""

def create_connection():
    """
    使用SQLAlchemy创建数据库连接
    """
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)
    return engine

def get_data_from_db(query: str) -> pd.DataFrame:
    """
    从数据库获取数据并返回为DataFrame
    """
    engine = create_connection()
    # 使用SQLAlchemy的引擎创建连接，并通过pandas读取SQL查询结果
    data = pd.read_sql(query, engine)
    return data

def store_prediction_results(results: List[Tuple[str, int]], table_name: str) -> None:
    """
    将模型预测结果存储到数据库中
    :param results: 模型预测结果的列表，每个元素为一个 (输入文本, 预测值) 元组
    :param table_name: 表的名称，用于插入数据
    """
    engine = create_connection()
    try:
        with engine.connect() as conn:
            insert_query = f"""
            INSERT INTO {table_name} (input_text, prediction_value)
            VALUES (:input_text, :prediction_value)
            """
            for input_text, prediction in results:
                conn.execute(text(insert_query), {
                    "input_text": input_text,
                    "prediction_value": prediction
                })
            conn.commit()
        print(f"Successfully inserted {len(results)} records into {table_name}.")
    except Exception as e:
        print(f"Error while inserting predictions: {e}")

    
def get_csv_data(file_path: str) -> pd.DataFrame:
    """
    从CSV文件加载数据
    """
    return pd.read_csv(file_path)

def load_csv_to_db(file_path: str, table_name: str) -> None:
    """
    从CSV文件加载数据并将其插入到数据库中的指定表
    """
    # 加载CSV数据
    data = get_csv_data(file_path)

    # 检查数据是否为空
    if data.empty:
        print("The CSV file is empty.")
        return

    # 创建数据库连接
    engine = create_connection()

    try:
        # 将数据插入数据库中的指定表
        data.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Data from {file_path} successfully inserted into {table_name}.")
        return True
    except Exception as e:
        print(f"Error while inserting data from CSV: {e}")
    
    return False


if __name__ == '__main__':
    load_csv_to_db('./data/JEOPARDY_CSV.csv', 'jeopardy')
