# FinMood/Stock-Market-Sentiment-Analysis-System 
# 股票市場情緒分析系統

為散戶投資人解決無法客觀量化市場輿論情緒以進行理性決策的問題。

---

## 為什麼做這個

痛點與目標：散戶交易容易受到新聞媒體與市場輿論的情緒影響，因此需要驗證這些情緒對前50大權值股股價的真實影響力（究竟是提前預警還是延遲反應。

三大數據解方：
- 指標化：利用大數據技術將雜亂的網路新聞「分數化」，轉換為可衡量的數據。
- 差異化(未來可優化)：橫向對比不同產業龍頭股，找出各產業對市場情緒的敏感度。
- 逆向化：在市場極端瘋狂（暴漲）或極端恐慌（暴跌）時，用客觀數據提供冷靜的反向思考，協助投資人理性決策。

---

## 系統架構
![alt text](image.png)

```
Source → Ingest → Storage → Process → Serve → Observe
```

把上面每個階段換成你們實際用的工具，例如：

| 階段 | 工具 |
|---|---|
| Source | {例：Spotify API / Kaggle CSV / 公開資料} |
| Ingest | Python |
| Storage | MySQL / MongoDB |
| Process | pandas / SQL |
| Serve | FastAPI / Streamlit |
| Observe | LINE Notify / Sentry |

---

## 環境需求

- **Python ≥ 3.12**（專案透過 `.python-version` 鎖定為 3.12）
- **[uv](https://docs.astral.sh/uv/)** — 快速的 Python 套件 / 專案管理工具

> [!IMPORTANT]
> 本專案以 `uv` 管理依賴（`pyproject.toml`），不使用傳統 `requirements.txt`。
> 若尚未安裝 uv，請先執行：
> ```bash
> # Windows (PowerShell)
> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
>
> # macOS / Linux
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

---

## 快速開始

```bash
git clone https://github.com/FinMood/Stock-Market-Sentiment-Analysis-System.git
cd Stock-Market-Sentiment-Analysis-System
cp .env.example .env   # 填入需要的 API keys
uv sync                # 自動建立 venv 並安裝所有依賴
uv run python main.py  # 透過 uv 執行（自動使用正確的 venv）
```

---

## 團隊
分工
Table 1 —> Table 3 : 2-3位(包含斷詞等處理)
Table 3+ Table 2 —> Table 4  ： 2-3位  (包含建立API)

| 成員 | 負責範圍 | GitHub |
|---|---|---|
| 王翠賢 | {標題清洗/Jieba斷詞/字典計分} | [翠賢github](https://github.com/Cuei-Sian) |
| 張凱宇 | {爬蟲} | https://github.com/HolaBaGa |
| {Name} | {負責什麼} | @user3 |

---

## 進度追蹤

見 [task.md](task.md)

---

## License

MIT
