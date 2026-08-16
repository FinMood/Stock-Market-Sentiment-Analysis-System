# INSERT資料
from crawler.mysql_connection import get_connection
import time
import pymysql

def save_news_to_mysql(df):

    if df.empty:
        print("⚠️ DataFrame 是空的，不寫入 MySQL")
        return 0

    # ========================================
    # DataFrame → List
    # ========================================

    data = []

    for _, row in df.iterrows():
        data.append(
            (
                row.get("date"),
                row.get("stock_id"),
                row.get("link"),
                row.get("source"),
                row.get("title"),
            )
        )

    sql = """
    INSERT IGNORE INTO news_raw
    (date, stock_id, link, source, title)
    VALUES (%s, %s, %s, %s, %s)
    """

    max_retry = 3

    # ========================================
    # MySQL Transaction Retry
    # ========================================

    for attempt in range(1, max_retry + 1):

        conn = None
        cursor = None

        try:

            print()
            print("🗄️ ====================================")
            print(
                f"🗄️ MySQL 寫入 "
                f"第 {attempt}/{max_retry} 次"
            )
            print("🗄️ ====================================")

            conn = get_connection()
            cursor = conn.cursor()

            print(
                f"📦 SQL 準備寫入："
                f"{len(data)} 筆"
            )

            cursor.executemany(
                sql,
                data
            )

            inserted_count = cursor.rowcount

            conn.commit()

            received_count = len(data)

            not_inserted_count = (
                received_count
                - inserted_count
            )

            print(
                f"💾 MySQL 執行完成 | "
                f"API資料：{received_count} 筆 | "
                f"新增：{inserted_count} 筆 | "
                f"未新增：{not_inserted_count} 筆"
            )

            return inserted_count

        except pymysql.MySQLError as e:

            if conn is not None:
                conn.rollback()

            # ====================================
            # Deadlock
            # ====================================

            error_code = e.args[0] if e.args else None

            if error_code == 1213:

                print(
                    f"⚠️ MySQL Deadlock | "
                    f"第 {attempt}/{max_retry} 次"
                )

                if attempt < max_retry:

                    wait_seconds = attempt * 2

                    print(
                        f"⏳ {wait_seconds} 秒後重試"
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

            # 不是 deadlock
            # 或 retry 已全部失敗
            raise

        finally:

            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

            print(
                "🔌 MySQL Connection 已關閉"
            )

    raise RuntimeError(
        "MySQL 寫入重試仍然失敗"
    )

def save_crawl_progress(
    stock_id,
    crawl_date,
    status,
    news_count
):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO crawl_progress
        (
            stock_id,
            crawl_date,
            status,
            news_count
        )
        VALUES (%s, %s, %s, %s)

        ON DUPLICATE KEY UPDATE
            status = VALUES(status),
            news_count = VALUES(news_count),
            updated_at = CURRENT_TIMESTAMP
        """

        cursor.execute(
            sql,
            (
                stock_id,
                crawl_date,
                status,
                news_count
            )
        )

        conn.commit()

        print(
            f"📍 Crawl Progress | "
            f"{stock_id} | "
            f"{crawl_date} | "
            f"{status} | "
            f"news={news_count}"
        )

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

def get_completed_stock_ids(crawl_date):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        SELECT stock_id
        FROM crawl_progress
        WHERE crawl_date = %s
          AND status IN ('success', 'no_news')
        """

        cursor.execute(
            sql,
            (crawl_date,)
        )

        rows = cursor.fetchall()

        completed_stock_ids = {
            str(row[0])
            for row in rows
        }

        print(
            f"📋 crawl_progress | "
            f"{crawl_date} 已完成："
            f"{len(completed_stock_ids)} 檔"
        )

        return completed_stock_ids

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

def is_crawl_completed(stock_id, crawl_date):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        SELECT 1
        FROM crawl_progress
        WHERE stock_id = %s
          AND crawl_date = %s
          AND status IN ('success', 'no_news')
        LIMIT 1
        """

        cursor.execute(
            sql,
            (
                stock_id,
                crawl_date
            )
        )

        result = cursor.fetchone()

        return result is not None

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()