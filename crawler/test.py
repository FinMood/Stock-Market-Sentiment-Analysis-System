import time
from crawler.worker import app

# ⚠️ 將這裡的名字改成跟 Worker [tasks] 裡面列出的一模一樣！
@app.task(name="crawler.tasks_finmind_news.crawler_finmind_news")
def simple_test_task():
    print("====================================")
    print("🔥 恭喜！Celery Worker 成功收到並執行了任務！")
    print("====================================")
    return "Success"

if __name__ == "__main__":
    print("🚀 正在發送簡單測試任務給 Celery...")
    simple_test_task.delay()
    print("✅ 任務已成功送入 RabbitMQ 佇列！")
