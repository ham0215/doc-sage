FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ ./src/

# データディレクトリの作成
RUN mkdir -p /app/data/documents /app/data/vectorstore

# Streamlitのポート
EXPOSE 8501

# ヘルスチェック
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Streamlitアプリの起動
ENTRYPOINT ["streamlit", "run", "src/ui/app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]