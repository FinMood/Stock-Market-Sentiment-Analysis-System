# INSERT資料
from crawler.mysql_connection import get_connection


def save_news_to_mysql(df):

    if df.empty:
        print("⚠️ DataFrame 是空的，不寫入 MySQL")
        return 0

    print()
    print("🗄️ ====================================")
    print("🗄️ 開始寫入 MySQL")
    print("🗄️ ====================================")
    print(f"準備寫入資料：{len(df)} 筆")

    conn = None
    cursor = None

    try:

        # ========================================
        # 建立 MySQL Connection
        # ========================================

        conn = get_connection()
        cursor = conn.cursor()

        # ========================================
        # MySQL Server 診斷
        # ========================================

        # cursor.execute("""
        #     SELECT
        #         @@hostname,
        #         @@port,
        #         DATABASE(),
        #         USER(),
        #         @@datadir
        # """)

        # mysql_info = cursor.fetchone()

        # print("🔍 MySQL Server 診斷")
        # print(f"   hostname = {mysql_info[0]}")
        # print(f"   port     = {mysql_info[1]}")
        # print(f"   database = {mysql_info[2]}")
        # print(f"   user     = {mysql_info[3]}")
        # print(f"   datadir  = {mysql_info[4]}")

        # ========================================
        # INSERT SQL
        # ========================================

        sql = """
        INSERT IGNORE INTO news_raw
        (date, stock_id, link, source, title)
        VALUES (%s, %s, %s, %s, %s)
        """

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

        print(f"📦 SQL 準備寫入：{len(data)} 筆")

        # ========================================
        # 寫入 MySQL
        # ========================================

        cursor.executemany(
            sql,
            data
        )

        # ★ 一定要先保存 INSERT 的 rowcount
        inserted_count = cursor.rowcount

        # ========================================
        # ★ 關鍵：正式提交 Transaction
        # ========================================

        conn.commit()

        # ========================================
        # 統計寫入結果
        # ========================================

        received_count = len(data)
        not_inserted_count = received_count - inserted_count

        print(
            f"💾 MySQL 執行完成 | "
            f"API資料：{received_count} 筆 | "
            f"新增：{inserted_count} 筆 | "
            f"未新增：{not_inserted_count} 筆"
        )
        return inserted_count
        # ========================================
        # 寫入後立即驗證整檔股票
        # ========================================

        # stock_id = str(df.iloc[0]["stock_id"])

        # cursor.execute(
        #     """
        #     SELECT
        #         COUNT(*),
        #         MIN(date),
        #         MAX(date)
        #     FROM news_raw
        #     WHERE stock_id = %s
        #     """,
        #     (stock_id,)
        # )

        # verify_result = cursor.fetchone()

        # print(
        #     f"🔎 DB立即驗證 | "
        #     f"stock_id={stock_id} | "
        #     f"目前總筆數={verify_result[0]} | "
        #     f"最早={verify_result[1]} | "
        #     f"最新={verify_result[2]}"
        # )

        # ========================================
        # 逐筆驗證
        # ========================================

        # print()
        # print("🔎 ===== MySQL 逐筆驗證 =====")

        # for _, row in df.iterrows():

        #     row_stock_id = str(row.get("stock_id"))
        #     news_date = row.get("date")
        #     title = row.get("title")
        #     link = row.get("link")

        #     cursor.execute(
        #         """
        #         SELECT
        #             date,
        #             stock_id,
        #             title,
        #             link
        #         FROM news_raw
        #         WHERE stock_id = %s
        #           AND link = %s
        #         LIMIT 1
        #         """,
        #         (
        #             row_stock_id,
        #             link
        #         )
        #     )

        #     result = cursor.fetchone()

        #     if result:

        #         print(
        #             f"✅ DB存在 | "
        #             f"{row_stock_id} | "
        #             f"{news_date} | "
        #             f"{title}"
        #         )

        #     else:

        #         print(
        #             f"❌ DB不存在 | "
        #             f"{row_stock_id} | "
        #             f"{news_date} | "
        #             f"{title}"
        #         )

        #         print(
        #             f"   link = {link}"
        #         )

        # print("🔎 ===============================")

        # return inserted_count

    except Exception as e:

        print()
        print("❌ ====================================")
        print("❌ MySQL 寫入失敗")
        print("❌ ====================================")
        print(f"錯誤類型：{type(e).__name__}")
        print(f"錯誤內容：{e}")
        print("❌ ====================================")

        if conn is not None:
            conn.rollback()

        raise

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

        print("🔌 MySQL Connection 已關閉")