# 使用yfinance  下載股價

from datetime import datetime, timedelta

import yfinance as yf
from celery import shared_task

from crawler.stock_price_repository import save_stock_price_to_mysql


def _to_python_number(value):
    """將 pandas / numpy 數值轉成可安全寫入 MySQL 的 Python scalar。"""
    if value is None:
        return None

    try:
        if value != value:  # NaN
            return None
    except Exception:
        pass

    if hasattr(value, "item"):
        return value.item()

    return value


def fetch_yahoo_daily_price(stock_id: str, date: str) -> dict | None:
    """
    抓取一檔台灣上市股票指定日期的 Yahoo Finance 日線行情。

    0050 成分股皆為 TWSE 上市股票，因此 Yahoo symbol 使用 <stock_id>.TW。
    yfinance 的 end 為 exclusive，所以單日查詢要用 date + 1 day。
    """

    stock_id = str(stock_id).strip()
    start_date = datetime.strptime(date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)
    yahoo_symbol = f"{stock_id}.TW"

    print()
    print("=" * 70)
    print("📈 Yahoo Finance 股價 Task 開始")
    print(f"📌 股票代碼：{stock_id}")
    print(f"🔎 Yahoo代碼：{yahoo_symbol}")
    print(f"📅 日期：{date}")
    print("=" * 70)

    ticker = yf.Ticker(yahoo_symbol)

    df = ticker.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        actions=True,
        repair=True,
        timeout=15,
        raise_errors=True,
    )

    if df.empty:
        print(f"⚠️ {stock_id} {date} Yahoo Finance 無交易資料")
        return None

    row = df.iloc[0]
    actual_trade_date = df.index[0].date().isoformat()

    price_data = {
        "trade_date": actual_trade_date,
        "stock_id": stock_id,
        "yahoo_symbol": yahoo_symbol,
        "open_price": _to_python_number(row.get("Open")),
        "high_price": _to_python_number(row.get("High")),
        "low_price": _to_python_number(row.get("Low")),
        "close_price": _to_python_number(row.get("Close")),
        "adj_close_price": _to_python_number(row.get("Adj Close")),
        "volume": _to_python_number(row.get("Volume")),
        "dividends": _to_python_number(row.get("Dividends")) or 0,
        "stock_splits": _to_python_number(row.get("Stock Splits")) or 0,
    }

    print(
        f"✅ Yahoo Finance 成功 | {stock_id} {actual_trade_date} | "
        f"O={price_data['open_price']} "
        f"H={price_data['high_price']} "
        f"L={price_data['low_price']} "
        f"C={price_data['close_price']} "
        f"V={price_data['volume']}"
    )

    return price_data


@shared_task(
    bind=True,
    name="tasks.get_stock_price",
    rate_limit="60/m",
    max_retries=3,
)
def get_stock_price(self, stock_id: str, date: str):
    """Celery Task：1 Task = 1 股票 × 1 日期。"""

    try:
        price_data = fetch_yahoo_daily_price(stock_id, date)

        if price_data is None:
            return {
                "stock_id": str(stock_id),
                "date": date,
                "status": "no_data",
            }

        save_stock_price_to_mysql(price_data)

        return {
            "stock_id": str(stock_id),
            "date": price_data["trade_date"],
            "status": "success",
            "close": price_data["close_price"],
        }

    except Exception as exc:
        print(
            f"❌ Yahoo Finance Task 失敗 | "
            f"{stock_id} {date} | {type(exc).__name__}: {exc}"
        )

        raise self.retry(
            exc=exc,
            countdown=min(60 * (2 ** self.request.retries), 600),
        )

from datetime import datetime, timedelta

import yfinance as yf
from celery import shared_task

from crawler.stock_price_repository import save_stock_price_to_mysql


@shared_task(
    bind=True,
    name="tasks.backfill_stock_price",
    rate_limit="20/m",
    max_retries=3,
)
def backfill_stock_price(
    self,
    stock_id: str,
    start_date: str,
    end_date: str,
):
    """
    Yahoo Finance 歷史股價 Backfill

    1 Task = 1 股票 × 一整段日期

    例如：
    2330
    2026-02-23 ~ 2026-08-17
    """

    stock_id = str(stock_id).strip()
    yahoo_symbol = f"{stock_id}.TW"

    print()
    print("=" * 70)
    print("📚 Yahoo Finance Backfill 開始")
    print(f"📌 股票代碼：{stock_id}")
    print(f"🔎 Yahoo代碼：{yahoo_symbol}")
    print(f"📅 日期範圍：{start_date} ~ {end_date}")
    print("=" * 70)

    try:

        # -------------------------------------------------
        # Yahoo 的 end 不包含當天
        # 所以 end_date 必須 +1 day
        # -------------------------------------------------

        end_dt = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ) + timedelta(days=1)

        yahoo_end_date = end_dt.strftime(
            "%Y-%m-%d"
        )

        # -------------------------------------------------
        # Yahoo Finance
        # -------------------------------------------------

        ticker = yf.Ticker(
            yahoo_symbol
        )

        df = ticker.history(
            start=start_date,
            end=yahoo_end_date,
            interval="1d",
            auto_adjust=False,
            actions=True,
            repair=True,
            timeout=30,
            raise_errors=True,
        )

        # -------------------------------------------------
        # 沒資料
        # -------------------------------------------------

        if df.empty:

            print(
                f"⚠️ {stock_id} "
                f"{start_date} ~ {end_date} "
                f"沒有股價資料"
            )

            return {
                "stock_id": stock_id,
                "status": "no_data",
                "count": 0,
            }

        # -------------------------------------------------
        # 每個交易日寫入 MySQL
        # -------------------------------------------------

        inserted_count = 0

        for trade_datetime, row in df.iterrows():

            trade_date = (
                trade_datetime
                .date()
                .isoformat()
            )

            price_data = {
                "trade_date": trade_date,

                "stock_id": stock_id,

                "yahoo_symbol": yahoo_symbol,

                "open_price":
                    _to_python_number(
                        row.get("Open")
                    ),

                "high_price":
                    _to_python_number(
                        row.get("High")
                    ),

                "low_price":
                    _to_python_number(
                        row.get("Low")
                    ),

                "close_price":
                    _to_python_number(
                        row.get("Close")
                    ),

                "adj_close_price":
                    _to_python_number(
                        row.get("Adj Close")
                    ),

                "volume":
                    _to_python_number(
                        row.get("Volume")
                    ),

                "dividends":
                    _to_python_number(
                        row.get("Dividends")
                    ) or 0,

                "stock_splits":
                    _to_python_number(
                        row.get("Stock Splits")
                    ) or 0,
            }

            save_stock_price_to_mysql(
                price_data
            )

            inserted_count += 1

        print()
        print("✅ ====================================")
        print("✅ Backfill 完成")
        print(f"股票：{stock_id}")
        print(
            f"Yahoo資料：{len(df)} 個交易日"
        )
        print(
            f"DB處理：{inserted_count} 筆"
        )
        print("=======================================")

        return {
            "stock_id": stock_id,
            "status": "success",
            "count": len(df),
            "start_date": start_date,
            "end_date": end_date,
        }

    except Exception as exc:

        print()
        print(
            f"❌ Backfill 失敗 | "
            f"{stock_id} | "
            f"{start_date} ~ {end_date}"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise self.retry(
            exc=exc,
            countdown=min(
                60 * (
                    2 ** self.request.retries
                ),
                600
            ),
        )