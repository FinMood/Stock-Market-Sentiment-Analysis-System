# INSERT資料

from crawler.mysql_connection import get_connection


def save_stock_price_to_mysql(price_data: dict) -> int:
    """將 Yahoo Finance 單日股價寫入 MySQL；同股票同日期重跑時更新資料。"""

    if not price_data:
        print("⚠️ price_data 是空的，不寫入 MySQL")
        return 0

    conn = None
    cursor = None

    sql = """
    INSERT INTO stock_price_daily (
        trade_date,
        stock_id,
        yahoo_symbol,
        open_price,
        high_price,
        low_price,
        close_price,
        adj_close_price,
        volume,
        dividends,
        stock_splits,
        source
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        yahoo_symbol = VALUES(yahoo_symbol),
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        adj_close_price = VALUES(adj_close_price),
        volume = VALUES(volume),
        dividends = VALUES(dividends),
        stock_splits = VALUES(stock_splits),
        source = VALUES(source)
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()

        values = (
            price_data["trade_date"],
            price_data["stock_id"],
            price_data["yahoo_symbol"],
            price_data.get("open_price"),
            price_data.get("high_price"),
            price_data.get("low_price"),
            price_data.get("close_price"),
            price_data.get("adj_close_price"),
            price_data.get("volume"),
            price_data.get("dividends", 0),
            price_data.get("stock_splits", 0),
            "Yahoo Finance",
        )

        cursor.execute(sql, values)
        affected_rows = cursor.rowcount
        conn.commit()

        print(
            f"💾 股價寫入完成 | "
            f"{price_data['stock_id']} | "
            f"{price_data['trade_date']} | "
            f"close={price_data.get('close_price')}"
        )

        return affected_rows

    except Exception:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()