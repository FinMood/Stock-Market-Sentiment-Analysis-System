# 偵測進度表 >避免重複寫入
CREATE TABLE crawl_progress (
    stock_id VARCHAR(10) NOT NULL,
    crawl_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    news_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (stock_id, crawl_date)
);

# 新聞表
CREATE TABLE news_raw ( 
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, 
    date DATETIME NOT NULL, 
    stock_id VARCHAR(10) NOT NULL, 
    link VARCHAR(700) NOT NULL, s
    ource VARCHAR(100), 
    title TEXT, 
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), UNIQUE KEY uk_stock_link (stock_id, link) 
);

# 每日股價表
CREATE TABLE IF NOT EXISTS stock_price_daily (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    trade_date DATE NOT NULL,
    stock_id VARCHAR(10) NOT NULL,
    yahoo_symbol VARCHAR(20) NOT NULL,

    open_price DECIMAL(18,4),
    high_price DECIMAL(18,4),
    low_price DECIMAL(18,4),
    close_price DECIMAL(18,4),
    adj_close_price DECIMAL(18,4),

    volume BIGINT UNSIGNED,

    dividends DECIMAL(18,6) DEFAULT 0,
    stock_splits DECIMAL(18,6) DEFAULT 0,

    source VARCHAR(30) NOT NULL DEFAULT 'Yahoo Finance',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_stock_trade_date (stock_id, trade_date),

    KEY idx_trade_date (trade_date),
    KEY idx_yahoo_symbol (yahoo_symbol)
);


# 清單固定 50 檔在SQL查缺少數量
SELECT
     crawl_date,
     COUNT(*) AS completed_count,
     50 - COUNT(*) AS missing_count
FROM crawl_progress
WHERE status IN ('success', 'no_news')
GROUP BY crawl_date
ORDER BY crawl_date;

# 查看沒有新聞的天數、平均新聞數
# AVG(news_count) 的分母是 crawl_progress 中實際存在的天數
SELECT
    stock_id,
    COUNT(*) AS completed_days,
    SUM(CASE WHEN news_count > 0 THEN 1 ELSE 0 END) AS days_with_news,
    SUM(news_count) AS total_news,
    ROUND(AVG(news_count), 2) AS avg_news_per_day,
    ROUND(
        AVG(CASE WHEN news_count > 0 THEN news_count END),
        2
    ) AS avg_news_when_has_news
FROM crawl_progress
WHERE status IN ('success', 'no_news')
GROUP BY stock_id
ORDER BY avg_news_per_day DESC;

# 進度
======
Milestone 1
✅ 單機 Celery + RabbitMQ + MySQL

Milestone 2
✅ Airflow 發任務
✅ Celery worker 執行
✅ crawl_progress
✅ repair_missing
✅ Deadlock retry

Milestone 3      ← 現在
⬜ date range parameter
⬜ 歷史 Backfill
⬜ 可斷點續跑
⬜ 2026-06-23 完整
⬜ 完成度 SQL 驗證

Milestone 4
⬜ GCP Compute Engine 正式部署
⬜ secrets / env
⬜ persistent storage
⬜ restart policy
⬜ logging

Milestone 5
⬜ 每日自動新聞更新

Milestone 6
⬜ 15 分鐘股價
⬜ 異常漲跌幅
⬜ LINE / notification