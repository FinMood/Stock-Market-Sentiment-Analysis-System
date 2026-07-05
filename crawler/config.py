import os

# RabbitMQ (訊息佇列) 登入帳密
WORKER_ACCOUNT = os.environ.get("WORKER_ACCOUNT", "NKR202")
WORKER_PASSWORD = os.environ.get("WORKER_PASSWORD", "p@ssw0rd")

# RabbitMQ 主機位址與通訊埠
# 127.0.0.1 代表本機, 若 RabbitMQ 跑在 docker 內, 要改成對應的 host
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
# int() 轉型是因為環境變數讀出來都是字串, 後續連線需要數字型別
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))

# MySQL 資料庫連線設定

