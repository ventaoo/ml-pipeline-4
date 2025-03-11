import os
import sys
import pytest
import pandas as pd

from sqlalchemy import inspect, text

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from db import create_connection, get_data_from_db, store_prediction_results, load_csv_to_db

# 测试数据库连接
@pytest.fixture
def db_connection():
    """
    Fixture for establishing a connection to the database.
    """
    engine = create_connection()
    yield engine
    # 在所有测试完成后关闭连接
    engine.dispose()

def test_load_csv_to_db():
    assert load_csv_to_db('./data/JEOPARDY_CSV.csv', 'jeopardy')

# 测试数据库连接是否成功
def test_create_connection(db_connection):
    """
    测试数据库连接是否成功
    """
    assert db_connection is not None
    
    # 使用inspect来检查表是否存在
    inspector = inspect(db_connection)
    assert 'jeopardy' in inspector.get_table_names()  # 检查'jeopardy'表是否存在

# 测试从数据库获取数据
def test_get_data_from_db(db_connection):
    """
    测试从数据库获取数据
    """
    query = f"SELECT * FROM {'jeopardy'} LIMIT 5;"  # 修改为实际表名
    data = get_data_from_db(query)
    assert isinstance(data, pd.DataFrame)
    assert not data.empty

def test_store_prediction_results(db_connection):
    """
    测试将预测结果存储到数据库
    """
    predictions = [("hello world", 1), ("machine learning", 2)]  # 模拟输入文本和预测结果
    store_prediction_results(predictions, 'predictions')  

    # 查询数据库获取插入的数据
    query = "SELECT input_text, prediction_value FROM predictions ORDER BY created_at DESC LIMIT 2;"
    with db_connection.connect() as conn:
        result = conn.execute(text(query)).fetchall()

    # 确保至少插入了 2 个结果
    assert len(result) == 2  

    # 校验插入的数据是否正确
    assert result[0] == predictions[0]  # 最新插入的应该匹配
    assert result[1] == predictions[1]