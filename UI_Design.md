# 前端 UI 設計與架構藍圖 (FastAPI + Streamlit)

> **這份文件定義了本系統儀表板 (Dashboard) 的設計規劃與實作藍圖，著重於將後端情緒分析與背離訊號結果進行視覺化與互動展示。**

---

## 🏗️ 系統架構：後端 API + 前端視覺化

系統將採分離式架構 (Decoupled Architecture)：
- **Backend (FastAPI)**：只負責讀取 `output/` 目錄下的合併資料（如 `divergence_signal_all.csv` 和 `percentile_thresholds.csv`），並以 JSON 格式提供 RESTful API，不處理視覺化。
- **Frontend (Streamlit)**：純粹做為 UI 渲染層，透過 `requests` 呼叫 FastAPI 端點，負責畫圖與資料互動。

---

## 📡 FastAPI 端點規劃 (Backend API)

API 端點將提供前端所需的所有資料緯度，預計實作以下 Endpoint：

| Endpoint | Method | 功能說明 | 返回資料結構預覽 |
|----------|--------|---------|-----------------|
| `/api/signals/all` | GET | 取得所有股票的每日綜合訊號與分數 | `[{date, stock_id, close, avg_sentiment, signal...}]` |
| `/api/signals/{stock_id}`| GET | 取得特定股票的時間序列資料 | `[{date, close, avg_sentiment, return_3d, signal...}]` |
| `/api/thresholds` | GET | 取得統整的統計門檻值 | `{ P10, P25, P75, P90 }` 分別對應股價與情緒 |
| `/api/history/{stock_id}`| GET | 取得各引擎的原始評分資料（供比較用）| `[{date, score_finbert, score_ckipbert, score_roberta, score_jieba}]` |

---

## 🖥️ Streamlit 前端網頁佈局 (UI Layout)

系統主要分為 3 個頁面 (Pages)，以側邊欄 (Sidebar) 進行導航：

### Page 1: 總覽與決策儀表板 (Overview Dashboard)
**目標：一眼看出目前個股的防呆狀態與相對位階。**

1. **頂部過濾器 (Header)**
   - 股票選擇 Dropdown (e.g., 2330 台積電, 2308 台達電)
   - 日期區間選擇 (Date Range)
   - **系統決策短評** (System Alert)

2. **核心圖表 (Main Chart)**
   - **情緒與股價疊加時間序列圖 (Time-Series Dual Axis)**
     - X軸：日期
     - Y1軸 (左)：股價 K 線 (Candlestick) 或折線圖
     - Y2軸 (右)：平均情緒分數 (`avg_sentiment`) 長條圖 (正綠/負紅)
     - *特殊標記*：在觸發「極端背離紅/綠燈」的日期上，標示明顯的 Icon

3. **市場位階儀表板 (Percentile Gauges)**
   - 兩個半圓形儀表板 (Gauge charts) 顯示最新一日的位階：
     - 左側：**情緒熱度** (極度悲觀 <- P10 ~ P90 -> 極度樂觀)
     - 右側：**近期漲跌** (大跌 <- P10 ~ P90 -> 大漲)

---

### Page 2: 歷史背離訊號分析 (Divergence Analysis)
**目標：透過歷史數據說服散戶「為何紅燈不能追、綠燈不要怕」。**

1. **訊號歷史軌跡 (Timeline)**
   - 列出過去一年內，該股票觸發紅/綠燈的次數與確切日期時間軸。

2. **回測勝率統計卡片 (Backtest Statistics)**
   - **紅燈過後跌幅機率** (e.g., 觸發紅燈後，未來 3 日內下跌機率 78%)
   - **綠燈過後反彈機率** (e.g., 觸發綠燈後，未來 3 日內反彈機率 65%)

3. **訊號歷史明細表 (Details Dataframe)**
   - 可排序、篩選的表格，包含欄位：`觸發日期`, `股價狀態`, `情緒分數`, `觸發訊號`, `後3日實際漲跌幅`。

---

### Page 3: 演算法引擎觀測站 (Engine Comparison) - [進階分析]
**目標：展示 4 大引擎 (FinBERT, CKIP-BERT, RoBERTa, Jieba) 的運作穩定性與一致性。**

1. **多模型情緒熱區分佈 (Heatmap)**
   - Y軸：引擎名稱
   - X軸：日期
   - 顏色深淺代表該引擎當天的預測情緒偏向。一眼看出哪些日子 4 個引擎全部看多，哪些日子出現分歧。

2. **引擎一致性長條圖 (Consensus Chart)**
   - 顯示每日的「意見一致率」。例如 4 個模型有 3 個看多，則一致率 = 75%。

---

## 🎨 視覺設計與色彩規範 (Color Palette)

- **主色調**：深色模式 (Dark Mode) 為主，減少散戶看盤的視覺疲勞。
- **訊號標示色**：
  - 極度樂觀 / 大漲 / 綠燈：`#10B981` (Emerald Green)
  - 極度悲觀 / 大跌 / 紅燈：`#EF4444` (Red)
  - 觀望 / 中性：`#F59E0B` (Amber/Yellow)
  - 輔助中性色：`#374151` (Gray 700) ~ `#9CA3AF` (Gray 400)

## 🚀 開發推動階段 (Implementation Steps)

- [ ] **Phase 1 (Data API)**: 以 `FastAPI` 實作資料端點，能正確讀取並 serving `divergence_signal_all.csv`。
- [ ] **Phase 2 (Basic UI)**: 用 `Streamlit` 串接 API，完成「Page 1: 總覽與決策儀表板」的圖表繪製。
- [ ] **Phase 3 (Analytics UI)**: 補齊 Page 2 與 Page 3 的歷史勝率表與多引擎熱力圖。
- [ ] **Phase 4 (Deployment)**: 包裝為 Docker Image，準備 GCP Cloud Run 部署。
