from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import uvicorn

app = FastAPI(
    title="Stock Sentiment Dashboard API",
    description="API to serve sentiment and divergence signals for the frontend dashboard",
    version="1.0.0"
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
OUTPUT_DIR = "output"
ALL_SIGNALS_FILE = os.path.join(OUTPUT_DIR, "divergence_signal_all.csv")
THRESHOLDS_FILE = os.path.join(OUTPUT_DIR, "percentile_thresholds.csv")

def safe_read_csv(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        return pd.read_csv(filepath, encoding="utf-8-sig")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Stock Sentiment Dashboard API is running."}

@app.get("/api/signals/all")
def get_all_signals():
    """取得所有股票的每日綜合訊號與分數"""
    df = safe_read_csv(ALL_SIGNALS_FILE)
    if df is None:
        raise HTTPException(status_code=404, detail="Signal data not found. Please run the ETL pipeline first.")
    
    import json
    return {"data": json.loads(df.to_json(orient="records"))}

@app.get("/api/signals/{stock_id}")
def get_stock_signals(stock_id: str):
    """取得特定股票的時間序列資料"""
    df = safe_read_csv(ALL_SIGNALS_FILE)
    if df is None:
        raise HTTPException(status_code=404, detail="Signal data not found.")
    
    # 先過濾該檔股票 (確保 stock_id 比較時都是字串)
    df["stock_id"] = df["stock_id"].astype(str)
    df_stock = df[df["stock_id"] == str(stock_id)]
    
    if df_stock.empty:
        raise HTTPException(status_code=404, detail=f"No data found for stock {stock_id}")

    import json
    return {"stock_id": stock_id, "data": json.loads(df_stock.to_json(orient="records"))}

@app.get("/api/thresholds")
def get_thresholds():
    """取得統整的統計門檻值"""
    df = safe_read_csv(THRESHOLDS_FILE)
    if df is None:
        raise HTTPException(status_code=404, detail="Threshold data not found.")
    
    import json
    return {"data": json.loads(df.to_json(orient="records"))}

if __name__ == "__main__":
    print("🚀 啟動 FastAPI 伺服器：http://localhost:8080")
    print("👉 Swagger UI：http://localhost:8080/docs")
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
