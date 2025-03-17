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
    input_text TEXT,
    prediction_value INT NOT NULL, -- 存储预测值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 存储记录的时间戳
);