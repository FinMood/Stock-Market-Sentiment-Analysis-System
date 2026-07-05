# 要記得安裝Celery 

from celery import Celery


# 從 config.py 讀取 RabbitMQ 連線資訊, Celery 透過它派送任務給 worker
from crawler.config import (
    RABBITMQ_HOST,  # RabbitMQ 主機位址, ex: localhost
    RABBITMQ_PORT,  # RabbitMQ 通訊埠, 預設 5672
    WORKER_ACCOUNT,  # 連線到 RabbitMQ 的帳號
    WORKER_PASSWORD,  # 連線到 RabbitMQ 的密碼
)


# 建立 Celery app 實例, "task" 是這個應用程式的名稱
app = Celery(
    "task",
    include=[
        "crawler.test",
        "crawler.tasks_finmind_news",  # 測試用
    ],
    broker=f"pyamqp://{WORKER_ACCOUNT}:{WORKER_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/",
)


# 正式啟用再做測試, 保險用
# app.conf.task_acks_late = True   # 預設 False
# app.conf.task_reject_on_worker_lost = True  # worker 掛掉時拒絕任務，重新排隊
