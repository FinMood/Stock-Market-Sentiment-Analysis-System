import sys
import os

# 將上一層目錄加入搜尋路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# 引入情緒分析層函數
import sentiment
from sentiment.jieba_sent_test_func_1 import jieba_sent_test_func
from sentiment.ckipbert_sent_test_func_1 import ckipbert_sent_test_func
from sentiment.finbert_sent_test_func_1 import finbert_sent_test_func
from sentiment.ckip_Transformers_test_func import ckip_Transformers_test_func
from sentiment.llm_sent_test_func import llm_sent_test_func
from sentiment.all_scores_func import all_scores_func

# 引入設定檔
import configs.all_config
# 引入輸入輸出資料夾/檔案設定
from configs.all_config import SOURCE_DIR, SCORE_DATA_DIR, OUTPUT_DIR, FINMIND_NEWS_DATA
# 引入情緒模型資料夾設定
from configs.all_config import NTUSD_DIR, CKIPBERT_DIR, FINBERT_DIR
# 引入情緒分數檔案名稱
from configs.all_config import JIEBA_SCORE, CKIPBERT_SCORE, FINBERT_SCORE, ROBERTA_SCORE, LLM_SCORE, SENT_ALL_SCORES
# 引入情緒模型設定
from configs.all_config import LLM_MODEL, CKIPBERT_PROC_SIZE, FINBERT_PROC_SIZE, LLM_MAX_RETRIES, LLM_BATCH_SLEEP



# define pipeline_sentiment_layer() as main()
def pipeline_sentiment_layer():
    
    ## parameters
    
    # use rel_dir to run on the subfolder
    rel_dir = "../"
    
    # use data_mode to test different source data from ['test', 'short20', 'short170']
    data_mode = "short20"
    data_fname_prefix = f"{FINMIND_NEWS_DATA}_{data_mode}"

    # source folder/files
    source_dir = os.path.join(rel_dir, SOURCE_DIR)
    news_title_fname = f"{data_fname_prefix}.csv"

    # score folder/files
    score_dir = os.path.join(rel_dir, SCORE_DATA_DIR)
    jieba_score_fname = f"{data_fname_prefix}_w_{JIEBA_SCORE}.csv"
    ckipbert_score_fname = f"{data_fname_prefix}_w_{CKIPBERT_SCORE}.csv"
    finbert_score_fname = f"{data_fname_prefix}_w_{FINBERT_SCORE}.csv"
    roberta_score_fname = f"{data_fname_prefix}_w_{ROBERTA_SCORE}.csv"
    llm_score_fname = f"{data_fname_prefix}_w_{LLM_SCORE}.csv"
    all_scores_fname = f"{data_fname_prefix}_w_{SENT_ALL_SCORES}.csv"

    # sent model parameters 
    ntusd_dir = os.path.join(rel_dir, NTUSD_DIR)
    ckip_model_dir = os.path.join(rel_dir, CKIPBERT_DIR)
    finbert_model_dir = os.path.join(rel_dir, FINBERT_DIR)


    ## Sentiment Layer ##
    # run sentiment functions
    # call jieba
    print("🚀 === 使用 Jieba & NTUSD 情緒字典進行評分 ===\n")
    jieba_sent_test_func(source_dir, ntusd_dir, score_dir, news_title_fname, jieba_score_fname)
    # call CKIP-BERT
    print("🚀 === 使用 CKIP-BERT & NTUSD 情緒字典進行評分 ===\n")
    ckipbert_sent_test_func(source_dir, ckip_model_dir, ntusd_dir, score_dir, news_title_fname, ckipbert_score_fname, CKIPBERT_PROC_SIZE)
    # call FinBERT
    print("🚀 === 使用 FinBERT 股市情緒模型進行評分 ===\n")
    finbert_sent_test_func(source_dir, finbert_model_dir, score_dir, news_title_fname, finbert_score_fname, FINBERT_PROC_SIZE)
    # call Roberta
    print("🚀 === 使用 RoBERTa 情緒模型進行評分 ===\n")
    ckip_Transformers_test_func(source_dir, news_title_fname, score_dir, roberta_score_fname)
    # call LLM 
    print("🚀 === 使用對話式 LLM 語言模型進行評分 ===\n")
    llm_sent_test_func(source_dir, news_title_fname, score_dir, llm_score_fname, LLM_MODEL, LLM_MAX_RETRIES, LLM_BATCH_SLEEP)
    
    # combine all scores 
    print("🚀 === 合併所有評分結果 ===\n")
    all_scores_func(source_dir, news_title_fname, score_dir, roberta_score_fname, ckipbert_score_fname, finbert_score_fname, jieba_score_fname, llm_score_fname, all_scores_fname)


if __name__ == "__main__":
    pipeline_sentiment_layer()