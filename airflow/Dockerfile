# 使用 Ubuntu 24.04 作為基礎映像檔（自帶 Python 3.12）
# 建立image docker build \ --no-cache \ --progress=plain \ -f airflow/Dockerfile \ -t stock-airflow:latest \ .

FROM ubuntu:24.04


# ========================================
# 系統套件
# ========================================

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# ========================================
# uv
# ========================================

ENV UV_SYSTEM_PYTHON=1
ENV UV_BREAK_SYSTEM_PACKAGES=1

RUN curl -LsSf https://astral.sh/uv/install.sh \
    | env UV_INSTALL_DIR=/usr/local/bin sh \
    && uv --version


# ========================================
# Google Cloud SDK
# ========================================

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && \
    apt-get install -y google-cloud-sdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# ========================================
# Airflow 目錄
# ========================================

RUN mkdir -p /opt/airflow


# ========================================
# 安裝 Airflow 2.10.4
#
# 強制 IPv4：
# 避免 raw.githubusercontent.com IPv6 連線問題
#
# --fail：
# HTTP 429 / 404 / 500 直接視為失敗，
# 不會把錯誤頁存成 constraints
# ========================================

RUN curl -4 -L \
    --fail \
    --retry 5 \
    --retry-delay 3 \
    --retry-all-errors \
    --connect-timeout 15 \
    "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.12.txt" \
    -o /tmp/constraints-3.12.txt \
    && echo "===== Airflow constraints 前 5 行 =====" \
    && head -5 /tmp/constraints-3.12.txt \
    && uv pip install --system \
        "apache-airflow[celery,google,docker,postgres]==2.10.4" \
        --constraint /tmp/constraints-3.12.txt


# ========================================
# 複製專案檔案
# ========================================

COPY pyproject.toml uv.lock README.md /opt/airflow/
COPY crawler /opt/airflow/crawler/

# GCP 憑證
# COPY key.json /opt/airflow/key.json


# ========================================
# 安裝專案本身
#
# --no-deps：
# 不讓 pyproject.toml 重新解析所有 dependencies，
# 避免影響 Airflow constraints
# ========================================

RUN cd /opt/airflow && \
    uv pip install --system -e . --no-deps


# ========================================
# 安裝專案 Runtime Dependencies
#
# 新增：
# yfinance
# scipy
# ========================================

RUN uv pip install --system \
    requests \
    pandas \
    loguru \
    celery \
    pymysql \
    "sqlalchemy==1.4.36" \
    "yfinance>=1.5.1" \
    "scipy>=1.18.0"


# ========================================
# Airflow Environment
# ========================================

ENV AIRFLOW_HOME=/opt/airflow

# ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/key.json

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Asia/Taipei


# ========================================
# Working Directory
# ========================================

WORKDIR /opt/airflow