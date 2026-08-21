import json
import os
import re
import sys
import time

import pandas as pd
from openai import OpenAI



## 定義一個函數 llm_sent_test_func()，方便串接專案
def llm_sent_test_func(io_input_dir, io_input_fname, io_output_dir, io_output_fname, llm_model_name, llm_max_retries=2, llm_batch_sleep=1.0):

#    PROJECT_ROOT = os.path.dirname(
#        os.path.dirname(
#            os.path.abspath(__file__)
#        )
#    )
#
#    if PROJECT_ROOT not in sys.path:
#        sys.path.insert(
#            0,
#            PROJECT_ROOT
#        )
#


    try:
        from llm_config import llm_config
    except ImportError:
        llm_config = None



    # ============================================================
    # 1. 基本設定
    # ============================================================

#    INPUT_FILE = os.path.join(
#        "source",
#        "TaiwanStockNews_test.csv"
#    )
#
#    OUTPUT_DIR = "score_data"
#
#    CACHE_FILE = os.path.join(
#        OUTPUT_DIR,
#        "llm_sentiment_cache.csv"
#    )

    INPUT_FILE = os.path.join(
        io_input_dir,
        io_input_fname
    )

    OUTPUT_DIR = io_output_dir

    io_cache_fname = io_output_fname.replace(".csv", "_cache.csv")
    CACHE_FILE = os.path.join(
        io_output_dir,
        io_cache_fname
    )
    

    # ------------------------------------------------------------
    # 測試範圍
    #
    # Python iloc：
    # TEST_START = 0
    # TEST_END   = 200
    #
    # 代表處理第 1～200 篇。
    #
    # 正式全部處理：
    #
    # TEST_START = None
    # TEST_END   = None
    # ------------------------------------------------------------

    TEST_START = None
    TEST_END = None


    # ------------------------------------------------------------
    # Batch 設定
    # ------------------------------------------------------------

    BATCH_SIZE = 50


    # ------------------------------------------------------------
    # API 重試
    # ------------------------------------------------------------

    ## 使用輸入的 llm_max_retries，增加程式的容錯率
#    MAX_RETRIES = 2
    MAX_RETRIES = llm_max_retries


    # ------------------------------------------------------------
    # 批次間等待
    # ------------------------------------------------------------

    ## 使用輸入的 llm_batch_sleep，增加程式的容錯率
#    BATCH_SLEEP = 1.0
    BATCH_SLEEP = llm_batch_sleep


    # ------------------------------------------------------------
    # 遇到 429 是否停止
    # ------------------------------------------------------------

    STOP_ON_RATE_LIMIT = True


    # ============================================================
    # 2. Groq API 初始化
    # ============================================================

    ## 使用輸入的模型 llm_model_name
    def init_ai_client(model_name):

        """
        初始化 Groq OpenAI-compatible API Client。

        llm_config.py 必須提供：

            GROQ_API_KEY = "gsk_..."
        """

        if llm_config is None:

            print(
                "⚠️ [API 初始化] 找不到 llm_config.py。"
            )

            return None, None


        groq_key = getattr(
            llm_config,
            "GROQ_API_KEY",
            ""
        )


        if not groq_key:

            print(
                "⚠️ [API 初始化] GROQ_API_KEY 未設定。"
            )

            return None, None

        if not groq_key.startswith("gsk_"):

            print(
                "⚠️ [API 初始化] GROQ_API_KEY 格式看起來不正確。"
            )

            return None, None

        try:

            client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )

            ## 使用輸入的模型 llm_model_name
#            model_name = "llama-3.1-8b-instant"

            print(
                f"🤖 [API 初始化] 啟用 Groq：{model_name}"
            )

            return client, model_name

        except Exception as e:

            print(
                f"❌ [API 初始化] Groq Client 建立失敗：{e}"
            )

            return None, None


    ## 使用輸入的 llm_model_name，以便之後更換使用的模型
#    client, MODEL_NAME = init_ai_client()
    client, MODEL_NAME = init_ai_client(llm_model_name)



    # ============================================================
    # 3. 輸入資料清洗
    # ============================================================

    def prepare_dataframe(df):

        df = df.copy()

        required_columns = [
            "stock_id",
            "title"
        ]

        for column in required_columns:

            if column not in df.columns:

                raise ValueError(
                    f"輸入資料缺少必要欄位：{column}"
                )

        original_count = len(df)

        # --------------------------------------------------------
        # stock_id
        # --------------------------------------------------------

        df["stock_id"] = (
            df["stock_id"]
            .astype(str)
            .str.strip()
        )

        before = len(df)

        df = df[
            df["stock_id"].notna()
            & (df["stock_id"] != "")
            & (df["stock_id"].str.lower() != "nan")
        ].copy()

        print(
            f"🧹 [資料清洗] 移除無 stock_id："
            f"{before - len(df)} 筆"
        )

        # --------------------------------------------------------
        # title
        # --------------------------------------------------------

        df["title"] = (
            df["title"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        before = len(df)

        df = df[
            df["title"] != ""
        ].copy()

        print(
            f"🧹 [資料清洗] 移除空標題："
            f"{before - len(df)} 筆"
        )

        # --------------------------------------------------------
        # 保留原始順序
        # --------------------------------------------------------

        df.reset_index(
            drop=True,
            inplace=True
        )

        print(
            f"📊 [資料清洗] 原始新聞數："
            f"{original_count}"
        )

        print(
            f"📊 [資料清洗] 清洗後新聞數："
            f"{len(df)}"
        )

        return df


    # ============================================================
    # 4. Cache Key
    # ============================================================

    def make_cache_key(
        stock_id,
        title
    ):

        stock_id = str(
            stock_id
        ).strip()

        title = str(
            title
        ).strip()

        return (
            f"{stock_id}|||{title}"
        )


    # ============================================================
    # 5. 建立 Prompt
    # ============================================================

    def build_prompt(batch_df):

        news_items = []

        for _, row in batch_df.iterrows():

            news_id = int(
                row["news_id"]
            )

            stock_id = str(
                row["stock_id"]
            ).strip()

            title = str(
                row["title"]
            ).strip()

            news_items.append(
                {
                    "id": news_id,
                    "stock_id": stock_id,
                    "title": title
                }
            )

        news_json = json.dumps(
            news_items,
            ensure_ascii=False,
            separators=(",", ":")
        )

        prompt = f"""
    你是台灣股票新聞情緒評分模型。

    請評估每筆新聞「對資料中指定 stock_id」的情緒影響。

    規則：

    1. stock_id 已由資料來源指定。
    2. 不得修改 stock_id。
    3. 不得重新分類新聞。
    4. 不得因標題提到其他公司而改變評分對象。
    5. stock_id 可以是任何股票或 ETF。
    6. 只評估新聞標題對指定 stock_id 的影響。
    7. 無明顯影響、無法判斷或中立時使用接近 0 的分數。
    8. score 必須介於 -1.0 到 1.0。

    分數定義：

    1.0  = 極度利多
    0.5  = 明顯利多
    0.2  = 輕微利多
    0.0  = 中立、無明顯影響或無法判斷
    -0.2 = 輕微利空
    -0.5 = 明顯利空
    -1.0 = 極度利空

    輸出規則：

    - 只能輸出 JSON Object。
    - 不要 Markdown。
    - 不要解釋。
    - 不要輸出分析過程。
    - 每個 id 必須出現一次。
    - 不可遺漏 id。
    - 不可新增 id。
    - scores 數量必須與輸入資料完全相同。
    - score 必須是數字。
    - score 必須介於 -1.0 到 1.0。
    - 不要輸出 stock_id。

    輸出格式：

    {{
    "scores":[
    {{"id":1,"score":0.25}},
    {{"id":2,"score":-0.30}}
    ]
    }}

    新聞資料：

    {news_json}
    """

        return prompt


    # ============================================================
    # 6. 解析 LLM Response
    # ============================================================

    def parse_llm_response(
        raw_content,
        expected_ids
    ):

        cleaned = raw_content.strip()

        # --------------------------------------------------------
        # 移除 Markdown code fence
        # --------------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

        # --------------------------------------------------------
        # JSON
        # --------------------------------------------------------

        try:

            data = json.loads(
                cleaned
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                f"LLM 回傳不是有效 JSON：{e}"
            )

        if not isinstance(
            data,
            dict
        ):

            raise ValueError(
                "LLM 回傳 JSON 不是 Object。"
            )

        if "scores" not in data:

            raise ValueError(
                "LLM 回傳缺少 scores 欄位。"
            )

        scores = data["scores"]

        if not isinstance(
            scores,
            list
        ):

            raise ValueError(
                "scores 必須是 List。"
            )

        expected_ids = list(
            expected_ids
        )

        # --------------------------------------------------------
        # 數量
        # --------------------------------------------------------

        if len(scores) != len(expected_ids):

            raise ValueError(
                "LLM 回傳數量錯誤："
                f"預期 {len(expected_ids)}，"
                f"實際 {len(scores)}"
            )

        result = {}

        # --------------------------------------------------------
        # 每筆檢查
        # --------------------------------------------------------

        for item in scores:

            if not isinstance(
                item,
                dict
            ):

                raise ValueError(
                    "scores 中存在非 Object 項目。"
                )

            if "id" not in item:

                raise ValueError(
                    "LLM 回傳項目缺少 id。"
                )

            if "score" not in item:

                raise ValueError(
                    "LLM 回傳項目缺少 score。"
                )

            try:

                news_id = int(
                    item["id"]
                )

                score = float(
                    item["score"]
                )

            except (
                TypeError,
                ValueError
            ):

                raise ValueError(
                    f"id 或 score 格式錯誤：{item}"
                )

            if news_id not in expected_ids:

                raise ValueError(
                    f"LLM 回傳不存在的 id："
                    f"{news_id}"
                )

            if news_id in result:

                raise ValueError(
                    f"LLM 重複回傳 id："
                    f"{news_id}"
                )

            if not -1.0 <= score <= 1.0:

                raise ValueError(
                    f"id={news_id} "
                    f"score 超出範圍："
                    f"{score}"
                )

            result[news_id] = round(
                score,
                2
            )

        # --------------------------------------------------------
        # 遺漏
        # --------------------------------------------------------

        missing_ids = (
            set(expected_ids)
            - set(result.keys())
        )

        if missing_ids:

            raise ValueError(
                f"LLM 遺漏 id："
                f"{sorted(missing_ids)}"
            )

        return result


    # ============================================================
    # 7. Rate Limit
    # ============================================================

    def print_rate_limit_info(response):

        try:

            headers = getattr(
                response,
                "headers",
                None
            )

            if headers is None:

                return

            remaining_tokens = headers.get(
                "x-ratelimit-remaining-tokens"
            )

            reset_tokens = headers.get(
                "x-ratelimit-reset-tokens"
            )

            remaining_requests = headers.get(
                "x-ratelimit-remaining-requests"
            )

            reset_requests = headers.get(
                "x-ratelimit-reset-requests"
            )

            print(
                "📊 [Groq Rate Limit]"
            )

            if remaining_tokens is not None:

                print(
                    f"   剩餘 Tokens："
                    f"{remaining_tokens}"
                )

            if reset_tokens is not None:

                print(
                    f"   Token Reset："
                    f"{reset_tokens}"
                )

            if remaining_requests is not None:

                print(
                    f"   剩餘 Requests："
                    f"{remaining_requests}"
                )

            if reset_requests is not None:

                print(
                    f"   Request Reset："
                    f"{reset_requests}"
                )

        except Exception:

            pass


    # ============================================================
    # 8. 單批 LLM 評分
    # ============================================================

    def get_llm_score_batch(
        batch_df
    ):

        if client is None or MODEL_NAME is None:

            raise RuntimeError(
                "Groq API Client 尚未成功初始化。"
            )

        expected_ids = (
            batch_df["news_id"]
            .astype(int)
            .tolist()
        )

        prompt = build_prompt(
            batch_df
        )

        for attempt in range(
            1,
            MAX_RETRIES + 1
        ):

            try:

                response = (
                    client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "你是嚴格遵守 JSON "
                                    "輸出格式的台灣股票新聞"
                                    "情緒評分模型。"
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.0,
                        response_format={
                            "type": "json_object"
                        }
                    )
                )

                # ------------------------------------------------
                # Rate Limit
                # ------------------------------------------------

                print_rate_limit_info(
                    response
                )

                # ------------------------------------------------
                # Token 使用量
                # ------------------------------------------------

                usage = getattr(
                    response,
                    "usage",
                    None
                )

                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0

                if usage is not None:

                    prompt_tokens = getattr(
                        usage,
                        "prompt_tokens",
                        0
                    ) or 0

                    completion_tokens = getattr(
                        usage,
                        "completion_tokens",
                        0
                    ) or 0

                    total_tokens = getattr(
                        usage,
                        "total_tokens",
                        0
                    ) or 0

                print(
                    f"🔢 [Token] "
                    f"Prompt={prompt_tokens} | "
                    f"Completion={completion_tokens} | "
                    f"Total={total_tokens}"
                )

                # ------------------------------------------------
                # Response
                # ------------------------------------------------

                raw_content = (
                    response
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                scores = parse_llm_response(
                    raw_content,
                    expected_ids
                )

                return (
                    scores,
                    {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "news_count": len(batch_df)
                    }
                )

            except Exception as e:

                error_text = str(e)

                is_rate_limit = (
                    "429" in error_text
                    or "rate limit" in error_text.lower()
                    or "tokens per day" in error_text.lower()
                    or "tokens per minute" in error_text.lower()
                )

                if is_rate_limit:

                    print(
                        "\n❌ [Groq Rate Limit]"
                    )

                    print(
                        error_text[:500]
                    )

                    if STOP_ON_RATE_LIMIT:

                        raise RuntimeError(
                            "GROQ_RATE_LIMIT"
                        )

                print(
                    f"⚠️ [LLM API] "
                    f"第 {attempt}/{MAX_RETRIES} 次失敗："
                    f"{error_text[:250]}"
                )

                if attempt < MAX_RETRIES:

                    wait_seconds = (
                        2.0 * attempt
                    )

                    print(
                        f"⏳ 等待 "
                        f"{wait_seconds:.1f} 秒後重試..."
                    )

                    time.sleep(
                        wait_seconds
                    )

        raise RuntimeError(
            "LLM 批次評分失敗，"
            "已達最大重試次數。"
        )


    # ============================================================
    # 9. Cache 載入
    # ============================================================

    def load_cache():

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        required_columns = [
            "cache_key",
            "stock_id",
            "title",
            "llm_score"
        ]

        if not os.path.exists(
            CACHE_FILE
        ):

            print(
                "📦 [快取] 建立新的 LLM 評分快取"
            )

            return pd.DataFrame(
                columns=required_columns
            )

        try:

            df_cache = pd.read_csv(
                CACHE_FILE,
                encoding="utf-8-sig"
            )

            if not all(
                column in df_cache.columns
                for column in required_columns
            ):

                print(
                    "⚠️ [快取] 格式不完整，重新建立。"
                )

                return pd.DataFrame(
                    columns=required_columns
                )

            df_cache = df_cache[
                required_columns
            ].copy()

            df_cache["cache_key"] = (
                df_cache["cache_key"]
                .astype(str)
            )

            df_cache["stock_id"] = (
                df_cache["stock_id"]
                .astype(str)
                .str.strip()
            )

            df_cache["title"] = (
                df_cache["title"]
                .fillna("")
                .astype(str)
            )

            df_cache["llm_score"] = pd.to_numeric(
                df_cache["llm_score"],
                errors="coerce"
            )

            df_cache = df_cache[
                df_cache["llm_score"].notna()
            ].copy()

            # ----------------------------------------------------
            # 同 cache_key 保留最後一筆
            # ----------------------------------------------------

            df_cache.drop_duplicates(
                subset=["cache_key"],
                keep="last",
                inplace=True
            )

            print(
                f"📦 [快取] 已載入："
                f"{len(df_cache)} 筆"
            )

            return df_cache

        except Exception as e:

            print(
                f"⚠️ [快取] 讀取失敗：{e}"
            )

            return pd.DataFrame(
                columns=required_columns
            )


    # ============================================================
    # 10. Cache 儲存
    # ============================================================

    def save_cache(
        df_cache
    ):

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        df_cache.to_csv(
            CACHE_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"💾 [Cache] 已儲存："
            f"{len(df_cache)} 筆"
        )


    # ============================================================
    # 11. 累積結果
    # ============================================================

    def load_existing_results():

#        result_file = os.path.join(
#            OUTPUT_DIR,
#            "llm_results.csv"
#        )
        result_file = os.path.join(
            io_output_dir,
            io_output_fname
        )

        if not os.path.exists(
            result_file
        ):

            return pd.DataFrame()

        try:

            df = pd.read_csv(
                result_file,
                encoding="utf-8-sig"
            )

            return df

        except Exception:

            return pd.DataFrame()


    # ============================================================
    # 12. 建立結果
    # ============================================================

    def build_result_dataframe(
        df,
        cache_dict
    ):

        result = df.copy()

        result["llm_score"] = (
            result["cache_key"]
            .map(cache_dict)
        )

        if result["llm_score"].isna().any():

            missing_count = int(
                result["llm_score"]
                .isna()
                .sum()
            )

            raise RuntimeError(
                f"仍有 {missing_count} 筆新聞"
                "找不到 LLM 評分。"
            )

        result["llm_score"] = (
            pd.to_numeric(
                result["llm_score"],
                errors="coerce"
            )
            .clip(-1.0, 1.0)
            .round(2)
        )

        return result


    # ============================================================
    # 13. 主分析
    # ============================================================

    # 新增變數 output_fname，以改變輸出名稱
    def analyze_and_save_csv(
        df,
        output_dir,
        output_fname
    ):

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        # --------------------------------------------------------
        # 13-1. 清洗
        # --------------------------------------------------------

        df = prepare_dataframe(
            df
        )

        # --------------------------------------------------------
        # 13-2. 測試範圍
        # --------------------------------------------------------

        if (
            TEST_START is not None
            and TEST_END is not None
        ):

            df = (
                df.iloc[
                    TEST_START:TEST_END
                ]
                .copy()
            )

            print(
                f"🧪 [測試模式] "
                f"處理第 "
                f"{TEST_START + 1}～{TEST_END} "
                f"篇新聞"
            )

        elif TEST_START is not None:

            df = (
                df.iloc[
                    TEST_START:
                ]
                .copy()
            )

            print(
                f"🧪 [測試模式] "
                f"從第 {TEST_START + 1} 篇開始"
            )

        # --------------------------------------------------------
        # 13-3. 沒有資料
        # --------------------------------------------------------

        if len(df) == 0:

            print(
                "⚠️ 沒有可處理的新聞。"
            )

            return df

        print(
            f"📊 [LLM] 本次新聞數："
            f"{len(df)}"
        )

        # --------------------------------------------------------
        # 13-4. 建立 news_id
        #
        # 從 1 開始，避免容易誤會 0-based index。
        # --------------------------------------------------------

        df = df.reset_index(
            drop=True
        )

        df["news_id"] = range(
            1,
            len(df) + 1
        )

        # --------------------------------------------------------
        # 13-5. Cache Key
        # --------------------------------------------------------

        df["cache_key"] = df.apply(
            lambda row:
            make_cache_key(
                row["stock_id"],
                row["title"]
            ),
            axis=1
        )

        # --------------------------------------------------------
        # 13-6. 載入 Cache
        # --------------------------------------------------------

        df_cache = load_cache()

        cache_dict = dict(
            zip(
                df_cache["cache_key"],
                df_cache["llm_score"]
            )
        )

        # --------------------------------------------------------
        # 13-7. 找出真正需要 LLM 評分的資料
        # --------------------------------------------------------

        df_new = df[
            ~df["cache_key"].isin(
                cache_dict.keys()
            )
        ].copy()

        print(
            "\n🔍 [新聞確認]"
        )

        print(
            f"   本次資料：{len(df)}"
        )

        print(
            f"   Cache 已有：{len(df) - len(df_new)}"
        )

        print(
            f"   真正待評分：{len(df_new)}"
        )

        # ========================================================
        # 13-8. LLM 批次評分
        # ========================================================

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        total_scored_news = 0

        if len(df_new) > 0:

            print(
                "\n🤖 [LLM] 開始 Groq 批次評分..."
            )

            total_new = len(df_new)

            for start in range(
                0,
                total_new,
                BATCH_SIZE
            ):

                end = min(
                    start + BATCH_SIZE,
                    total_new
                )

                batch_df = (
                    df_new
                    .iloc[start:end]
                    .copy()
                )

                print(
                    "\n"
                    + "=" * 60
                )

                print(
                    f"📦 [Batch] "
                    f"{start + 1}～{end} / "
                    f"{total_new}"
                )

                try:

                    batch_scores, usage_info = (
                        get_llm_score_batch(
                            batch_df
                        )
                    )

                except RuntimeError as e:

                    if str(e) == "GROQ_RATE_LIMIT":

                        print(
                            "\n🛑 [流程停止]"
                        )

                        print(
                            "目前已完成的 Batch 已寫入 Cache。"
                        )

                        raise

                    raise

                # ------------------------------------------------
                # 累積 Token
                # ------------------------------------------------

                total_prompt_tokens += (
                    usage_info["prompt_tokens"]
                )

                total_completion_tokens += (
                    usage_info["completion_tokens"]
                )

                total_tokens += (
                    usage_info["total_tokens"]
                )

                total_scored_news += (
                    usage_info["news_count"]
                )

                # ------------------------------------------------
                # 將分數寫回 batch
                # ------------------------------------------------

                batch_df["llm_score"] = (
                    batch_df["news_id"]
                    .map(batch_scores)
                )

                if batch_df["llm_score"].isna().any():

                    raise RuntimeError(
                        "Batch 完成後仍有新聞沒有分數。"
                    )

                # ------------------------------------------------
                # 每批立即更新 Cache
                # ------------------------------------------------

                batch_cache = batch_df[
                    [
                        "cache_key",
                        "stock_id",
                        "title",
                        "llm_score"
                    ]
                ].copy()

                df_cache = pd.concat(
                    [
                        df_cache,
                        batch_cache
                    ],
                    ignore_index=True
                )

                df_cache.drop_duplicates(
                    subset=["cache_key"],
                    keep="last",
                    inplace=True
                )

                save_cache(
                    df_cache
                )

                # ------------------------------------------------
                # 更新記憶體 Cache
                # ------------------------------------------------

                cache_dict = dict(
                    zip(
                        df_cache["cache_key"],
                        df_cache["llm_score"]
                    )
                )

                # ------------------------------------------------
                # 每批 Token 統計
                # ------------------------------------------------

                batch_total_tokens = (
                    usage_info["total_tokens"]
                )

                batch_news_count = (
                    usage_info["news_count"]
                )

                if batch_news_count > 0:

                    avg_tokens = (
                        batch_total_tokens
                        / batch_news_count
                    )

                else:

                    avg_tokens = 0

                print(
                    f"📊 [Batch Token]"
                    f" 每篇平均："
                    f"{avg_tokens:.1f}"
                )

                # ------------------------------------------------
                # 批次間等待
                # ------------------------------------------------

                if end < total_new:

                    time.sleep(
                        BATCH_SLEEP
                    )

        else:

            print(
                "\n⚡ [Cache] "
                "本次所有新聞都已有評分，"
                "不重新呼叫 LLM。"
            )

        # ========================================================
        # 13-9. 將 Cache 分數對回本次資料
        # ========================================================

        output_df = build_result_dataframe(
            df,
            cache_dict
        )

        # ========================================================
        # 13-10. 移除內部欄位
        # ========================================================

        output_df = output_df.drop(
            columns=[
                "cache_key",
                "news_id"
            ],
            errors="ignore"
        ).copy()

        # ========================================================
        # 13-11. 輸出結果
        #
        # 注意：
        #
        # 這裡輸出的就是「本次 TEST_START～TEST_END」。
        #
        # Cache 則保存所有歷次完成的評分。
        # ========================================================

#        llm_output_file = os.path.join(
#            output_dir,
#            "llm_results.csv"
#        )
#
#        report_output_file = os.path.join(
#            output_dir,
#            "news_sentiment_report.csv"
#        )

        llm_output_file = os.path.join(
            output_dir,
            output_fname
        )

        report_fname = output_fname.replace(".csv", "_report.csv")
        report_output_file = os.path.join(
            output_dir,
            report_fname
        )

        output_df.to_csv(
            llm_output_file,
            index=False,
            encoding="utf-8-sig"
        )

        output_df.to_csv(
            report_output_file,
            index=False,
            encoding="utf-8-sig"
        )

        # ========================================================
        # 13-12. Token 統計
        # ========================================================

        print(
            "\n"
            + "=" * 60
        )

        print(
            "📊 [本次 LLM Token 統計]"
        )

        print(
            f"   新增評分新聞："
            f"{total_scored_news}"
        )

        print(
            f"   Prompt Tokens："
            f"{total_prompt_tokens}"
        )

        print(
            f"   Completion Tokens："
            f"{total_completion_tokens}"
        )

        print(
            f"   Total Tokens："
            f"{total_tokens}"
        )

        if total_scored_news > 0:

            print(
                f"   平均每篇 Token："
                f"{total_tokens / total_scored_news:.2f}"
            )

            print(
                f"   平均每篇 Prompt Token："
                f"{total_prompt_tokens / total_scored_news:.2f}"
            )

            print(
                f"   平均每篇 Completion Token："
                f"{total_completion_tokens / total_scored_news:.2f}"
            )

        print(
            "\n📊 [儲存完成]"
        )

        print(
            f"   LLM 結果："
            f"{llm_output_file}"
        )

        print(
            f"   總報表："
            f"{report_output_file}"
        )

        print(
            f"   本次輸出："
            f"{len(output_df)} 筆"
        )

        print(
            f"   Cache 總數："
            f"{len(df_cache)} 筆"
        )

        print(
            "=" * 60
        )

        return output_df


    # ============================================================
    # 14. Main
    # ============================================================

#
# 在函數中，移掉 if __name__ == "__main__":
#
#    if __name__ == "__main__":

    print(
        "🚀 === LLM 新聞情緒評分 ==="
    )

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    if client is None:

        print(
            "❌ Groq API Client 尚未成功初始化。"
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    if not os.path.exists(
        INPUT_FILE
    ):

        print(
            f"❌ 找不到新聞原始檔案："
            f"{INPUT_FILE}"
        )

        raise SystemExit(1)

    print(
        f"📂 正在讀取："
        f"{INPUT_FILE}"
    )

    raw_df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print(
        f"📊 原始新聞數："
        f"{len(raw_df)}"
    )

    # --------------------------------------------------------
    # Run
    # --------------------------------------------------------

    try:

#        analyze_and_save_csv(
#            raw_df,
#            output_dir=OUTPUT_DIR
#        )
        analyze_and_save_csv(
            raw_df,
            output_dir=io_output_dir,
            output_fname=io_output_fname
        )

    except RuntimeError as e:

        if str(e) == "GROQ_RATE_LIMIT":

            print(
                "\n"
                + "=" * 60
            )

            print(
                "🛑 Groq 免費額度已達限制。"
            )

            print(
                "已完成的 Batch 已寫入 Cache。"
            )

            print(
                "額度恢復後重新執行即可繼續。"
            )

            print(
                "=" * 60
            )

            raise SystemExit(2)

        raise