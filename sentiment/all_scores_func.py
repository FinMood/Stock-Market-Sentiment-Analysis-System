import pandas as pd



def all_scores_func(news_dir, news_fname, score_dir, roberta_fname, ckipbert_fname, finbert_fname, jieba_fname, llm_fname, output_fname):

    # --- 整合五個模型的分數 ---
    # 1. 讀取原始新聞資料檔
    df_final = pd.read_csv(f"{news_dir}/{news_fname}")

    # 2. 依序讀取五個模型的 CSV 並將最後一欄 score 提取出來寫入
    df_Roberta = pd.read_csv(f"{score_dir}/{roberta_fname}")
    df_ckipbert = pd.read_csv(f"{score_dir}/{ckipbert_fname}")
    df_finbert = pd.read_csv(f"{score_dir}/{finbert_fname}")
    df_jieba = pd.read_csv(f"{score_dir}/{jieba_fname}")
    df_llm = pd.read_csv(f"{score_dir}/{llm_fname}")

    # 3. 新增五個對應的模型分數欄位
    # 翠賢模型
    df_final["score_Roberta"] = df_Roberta["score_normalized"]
    # 至得模型
    df_final["score_ckipbert"] = df_ckipbert["score"]
    df_final["score_finbert"] = df_finbert["score"]
    df_final["score_jieba"] = df_jieba["score"]
    #JOY模型(LLM)
    df_final["score_llm"] = df_llm["llm_score"]

    # 4. 寫入並儲存至 score_data 資料夾
    df_final.to_csv(
        f"{score_dir}/{output_fname}",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"🎉 完美整合！五個模型的分數已成功寫入 {output_fname}")

