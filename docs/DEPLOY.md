# 🚀 Doc Sage デプロイガイド

このガイドでは、Doc Sageを本番環境にデプロイする手順を説明します。

## 目次

- [デプロイ前のチェックリスト](#デプロイ前のチェックリスト)
- [ローカル環境でのテスト](#ローカル環境でのテスト)
- [本番環境へのデプロイ](#本番環境へのデプロイ)
- [環境別の設定](#環境別の設定)
- [トラブルシューティング](#トラブルシューティング)

## デプロイ前のチェックリスト

### 必須要件

- [ ] Docker & Docker Compose がインストールされている
- [ ] OpenAI APIキーを取得済み
- [ ] `.env`ファイルを作成し、必要な環境変数を設定
- [ ] ポート8501が利用可能
- [ ] 十分なディスクスペース（最低10GB推奨）

### 推奨要件

- [ ] バックアップ戦略を策定
- [ ] ログ監視ツールの準備
- [ ] SSL/TLS証明書の準備（本番環境の場合）
- [ ] リバースプロキシの設定（Nginx等）

## ローカル環境でのテスト

### 1. リポジトリのクローン

```bash
git clone https://github.com/ham0215/doc-sage.git
cd doc-sage
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```env
OPENAI_API_KEY=sk-your-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHROMA_PERSIST_DIRECTORY=/app/data/vectorstore
DB_PATH=/app/data/doc-sage.db
LOG_LEVEL=INFO
```

### 3. ビルドと起動

```bash
# ビルド
docker compose build

# 起動
docker compose up
```

### 4. 動作確認

1. ブラウザで http://localhost:8501 を開く
2. テスト用PDFファイルをアップロード
3. 質問を入力して回答を確認
4. 参照元が正しく表示されることを確認

### 5. ログの確認

```bash
# ログをリアルタイムで確認
docker compose logs -f

# 特定のサービスのログのみ
docker compose logs -f doc-sage
```

## 本番環境へのデプロイ

### Option 1: Docker Composeで直接デプロイ

#### ステップ1: サーバーの準備

```bash
# サーバーにSSH接続
ssh user@your-server.com

# 必要なツールのインストール
sudo apt update
sudo apt install -y docker.io docker-compose git

# Dockerの起動
sudo systemctl start docker
sudo systemctl enable docker
```

#### ステップ2: デプロイ

```bash
# リポジトリのクローン
git clone https://github.com/ham0215/doc-sage.git
cd doc-sage

# 環境変数の設定
cp .env.example .env
vim .env  # APIキー等を設定

# データディレクトリの作成と権限設定
mkdir -p data/documents data/vectorstore
chmod -R 755 data

# ビルドと起動
sudo docker compose up -d

# 起動確認
sudo docker compose ps
```

#### ステップ3: リバースプロキシの設定（推奨）

Nginxを使用する例：

```nginx
# /etc/nginx/sites-available/doc-sage
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Streamlit
        proxy_read_timeout 86400;
    }
}
```

有効化：

```bash
sudo ln -s /etc/nginx/sites-available/doc-sage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### ステップ4: SSL/TLS証明書の設定

Let's Encryptを使用する例：

```bash
# Certbotのインストール
sudo apt install -y certbot python3-certbot-nginx

# 証明書の取得
sudo certbot --nginx -d your-domain.com

# 自動更新の設定
sudo certbot renew --dry-run
```

### Option 2: クラウドプラットフォームへのデプロイ

#### AWS ECS

```bash
# ECRにイメージをプッシュ
aws ecr create-repository --repository-name doc-sage
docker build -t doc-sage .
docker tag doc-sage:latest YOUR_ECR_URI/doc-sage:latest
docker push YOUR_ECR_URI/doc-sage:latest

# ECSタスク定義とサービスの作成
# （AWSコンソールまたはTerraformで設定）
```

#### Google Cloud Run

```bash
# イメージのビルドとプッシュ
gcloud builds submit --tag gcr.io/PROJECT_ID/doc-sage

# デプロイ
gcloud run deploy doc-sage \
  --image gcr.io/PROJECT_ID/doc-sage \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

#### Heroku

```bash
# Herokuアプリの作成
heroku create your-app-name

# 環境変数の設定
heroku config:set OPENAI_API_KEY=your-key

# デプロイ
git push heroku main
```

## 環境別の設定

### 開発環境

```yaml
# compose.dev.yaml を使用
docker compose -f compose.dev.yaml up
```

特徴：
- ホットリロード有効
- デバッグログ出力（LOG_LEVEL=DEBUG）
- ソースコードがマウントされる

### 本番環境

```yaml
# compose.yaml を使用
docker compose up -d
```

特徴：
- 最適化されたイメージ
- LOG_LEVEL=INFO
- 自動再起動設定

### ステージング環境

本番環境と同じ設定で、異なるドメインで運用：

```bash
# 環境変数で分離
cp .env .env.staging
# .env.staging を編集

# 起動
docker compose --env-file .env.staging up -d
```

## メンテナンス

### バックアップ

```bash
# データディレクトリのバックアップ
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 定期バックアップのcron設定
0 2 * * * cd /path/to/doc-sage && tar -czf ~/backups/doc-sage-$(date +\%Y\%m\%d).tar.gz data/
```

### アップデート

```bash
# 最新コードの取得
git pull origin main

# イメージの再ビルド
docker compose build --no-cache

# 再起動
docker compose down
docker compose up -d
```

### ログローテーション

```bash
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
# Dockerの再起動
sudo systemctl restart docker
```

### 監視

Prometheusとの統合例：

```yaml
# compose.yaml に追加
services:
  doc-sage:
    # ... 既存の設定 ...
    labels:
      - "prometheus-job=doc-sage"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

## スケーリング

### 垂直スケーリング

リソース制限の調整：

```yaml
# compose.yaml
services:
  doc-sage:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 水平スケーリング

ロードバランサーを使用：

```bash
# 複数インスタンスの起動
docker compose up -d --scale doc-sage=3
```

Nginxでのロードバランシング：

```nginx
upstream doc_sage {
    least_conn;
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}

server {
    location / {
        proxy_pass http://doc_sage;
    }
}
```

## セキュリティ

### 基本的なセキュリティ対策

1. **APIキーの保護**
   ```bash
   # 環境変数ファイルの権限
   chmod 600 .env
   ```

2. **ファイアウォール設定**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **定期的なアップデート**
   ```bash
   # システムパッケージ
   sudo apt update && sudo apt upgrade -y

   # Dockerイメージ
   docker compose pull
   docker compose up -d
   ```

4. **アクセス制限**
   - Basic認証の追加
   - IP制限の設定
   - VPN経由のアクセスのみ許可

### データ暗号化

```bash
# ボリュームの暗号化（Linux）
sudo cryptsetup luksFormat /dev/sdX
sudo cryptsetup luksOpen /dev/sdX doc-sage-data
sudo mkfs.ext4 /dev/mapper/doc-sage-data
```

## トラブルシューティング

### コンテナが起動しない

```bash
# ログの確認
docker compose logs

# コンテナの状態確認
docker compose ps

# イメージの再ビルド
docker compose build --no-cache
docker compose up -d
```

### ポート競合

```yaml
# compose.yaml でポート変更
ports:
  - "8502:8501"  # 8501の代わりに8502を使用
```

### メモリ不足

```bash
# Dockerのメモリ制限を増やす
# Docker Desktop: Settings > Resources > Memory

# コンテナのメモリ使用状況確認
docker stats
```

### データベースエラー

```bash
# データベースの再初期化
docker compose down
rm data/doc-sage.db
docker compose up -d
```

## パフォーマンス最適化

### Dockerイメージの最適化

```dockerfile
# multi-stage buildの使用
FROM python:3.11-slim as builder
# ... ビルド処理 ...

FROM python:3.11-slim
COPY --from=builder /app /app
```

### キャッシュの活用

```bash
# Buildkit の有効化
export DOCKER_BUILDKIT=1
docker compose build
```

### ヘルスチェックの調整

```yaml
# compose.yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 本番環境チェックリスト

デプロイ前に以下を確認：

- [ ] 環境変数が正しく設定されている
- [ ] バックアップが機能している
- [ ] ログ監視が設定されている
- [ ] SSL証明書が有効
- [ ] ファイアウォールが適切に設定されている
- [ ] リソース制限が設定されている
- [ ] ヘルスチェックが機能している
- [ ] 緊急時の連絡先とロールバック手順が文書化されている

## サポート

問題が発生した場合：

1. [GitHub Issues](https://github.com/ham0215/doc-sage/issues) で報告
2. ログを添付（個人情報は削除）
3. 環境情報を記載（OS、Dockerバージョン等）

---

**ドキュメントバージョン:** 1.0
**最終更新:** 2025-10-01
