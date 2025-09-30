# doc-sage MVP開発計画

## プロジェクト概要

**プロジェクト名:** doc-sage
**目的:** PDFドキュメントに対してAIで質問応答ができるチャットボット（将来的に動画・音声にも対応予定）
**技術スタック:** LangChain + Streamlit + Docker
**開発フェーズ:** MVP（最小実行可能製品）

---

## システム構成

### アーキテクチャ図

```
┌─────────────────────────────────────────┐
│         Frontend (Streamlit)            │
│  - ファイルアップロード                 │
│  - チャット画面                         │
│  - 会話履歴表示                         │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│      LangChain Processing Layer         │
│                                          │
│  ┌────────────────────────────────┐   │
│  │  Document Loaders              │   │
│  │  - PyPDFLoader                 │   │
│  └────────────────────────────────┘   │
│              ↓                          │
│  ┌────────────────────────────────┐   │
│  │  Text Splitter                 │   │
│  │  - RecursiveCharacterText...   │   │
│  └────────────────────────────────┘   │
│              ↓                          │
│  ┌────────────────────────────────┐   │
│  │  Embeddings                    │   │
│  │  - OpenAI Embeddings           │   │
│  └────────────────────────────────┘   │
│              ↓                          │
│  ┌────────────────────────────────┐   │
│  │  Vector Store (Chroma)         │   │
│  │  - ローカル永続化              │   │
│  └────────────────────────────────┘   │
│              ↓                          │
│  ┌────────────────────────────────┐   │
│  │  Retriever & QA Chain          │   │
│  │  - 類似度検索 + LLM回答生成   │   │
│  └────────────────────────────────┘   │
└──────────────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│          Storage Layer                  │
│                                          │
│  ┌────────────────────────────────┐   │
│  │  SQLite                        │   │
│  │  - 会話履歴                    │   │
│  │  - ドキュメント管理            │   │
│  └────────────────────────────────┘   │
│                                          │
│  ┌────────────────────────────────┐   │
│  │  Chroma (VectorDB)             │   │
│  │  - ベクトルデータ永続化        │   │
│  └────────────────────────────────┘   │
│                                          │
│  ┌────────────────────────────────┐   │
│  │  File Storage                  │   │
│  │  - アップロードファイル        │   │
│  └────────────────────────────────┘   │
└──────────────────────────────────────┘
```

---

## 技術スタック

### MVP構成

| カテゴリ | 技術 | 理由 |
|---------|------|------|
| **UI** | Streamlit | 最速で実装可能、Pythonのみで完結 |
| **LLM** | OpenAI GPT-3.5/4 | 安定性・性能が高い |
| **Embeddings** | OpenAI Embeddings | LLMと同じプロバイダで統一 |
| **Vector DB** | Chroma | セットアップ簡単、無料 |
| **Database** | SQLite | 軽量、ファイルベース、簡単 |
| **Framework** | LangChain | RAG構築の標準フレームワーク |
| **Container** | Docker | 環境の一貫性、簡単デプロイ |

### 主要ライブラリ

```
langchain==0.1.0
langchain-openai==0.0.5
chromadb==0.4.22
pypdf==4.0.1
streamlit==1.31.0
sqlalchemy==2.0.25
python-dotenv==1.0.1
```

---

## ディレクトリ構成

```
doc-sage/
├── compose.yaml              # Docker Compose設定
├── compose.dev.yaml          # 開発用Docker設定
├── Dockerfile                # Dockerイメージ定義
├── requirements.txt          # Python依存関係
├── .env.example              # 環境変数テンプレート
├── .env                      # 環境変数（gitignore）
├── .dockerignore             # Docker除外ファイル
├── .gitignore                # Git除外ファイル
├── README.md                 # プロジェクト説明
│
├── src/                      # ソースコード
│   ├── __init__.py
│   ├── main.py               # エントリーポイント
│   ├── config.py             # 設定管理
│   │
│   ├── database/             # データベース層
│   │   ├── __init__.py
│   │   ├── models.py         # SQLAlchemyモデル
│   │   ├── crud.py           # CRUD操作
│   │   └── init_db.py        # DB初期化
│   │
│   ├── loaders/              # ドキュメントローダー
│   │   ├── __init__.py
│   │   ├── pdf_loader.py     # PDF読み込み
│   │   └── base_loader.py    # 共通インターフェース
│   │
│   ├── processing/           # 処理ロジック
│   │   ├── __init__.py
│   │   ├── text_splitter.py  # テキスト分割
│   │   ├── embeddings.py     # 埋め込み生成
│   │   └── vectorstore.py    # ベクトルストア管理
│   │
│   ├── chains/               # LangChainチェーン
│   │   ├── __init__.py
│   │   ├── qa_chain.py       # QAチェーン
│   │   └── memory.py         # 会話メモリ
│   │
│   └── ui/                   # ユーザーインターフェース
│       ├── __init__.py
│       └── app.py            # Streamlitアプリ
│
├── data/                     # データ保存（Dockerボリューム）
│   ├── documents/            # アップロードファイル
│   ├── vectorstore/          # Chromaデータ
│   └── doc-sage.db           # SQLiteデータベース
│
├── tests/                    # テストコード
│   ├── __init__.py
│   ├── test_loaders.py
│   ├── test_processing.py
│   └── test_chains.py
│
└── notebooks/                # 実験・プロトタイプ
    └── prototype.ipynb
```

---

## データベース設計

### SQLiteテーブル構成

#### 1. documents テーブル
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    status TEXT DEFAULT 'processing'  -- processing, completed, failed
);
```

#### 2. conversations テーブル
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    document_id INTEGER,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

#### 3. document_chunks テーブル（オプション）
```sql
CREATE TABLE document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    vector_id TEXT,  -- ChromaのドキュメントID
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

---

## VectorDBの役割

### SQLite vs VectorDB（Chroma）

| 項目 | SQLite | VectorDB (Chroma) |
|------|--------|-------------------|
| **保存データ** | メタデータ、履歴、管理情報 | テキストの意味（ベクトル） |
| **検索方法** | 完全一致、LIKE検索 | 意味的類似度検索 |
| **データ例** | ファイル名、日時、ユーザーID | "犬について..." → [0.23, -0.45, ...] |
| **用途** | 管理、記録、リレーション | コンテンツの意味検索 |

### VectorDBの処理フロー

```
【入力】
"犬の特徴について教えて"

【VectorDBでの処理】
1. 質問をベクトル化: [0.23, -0.45, 0.78, ...]
2. ドキュメント内の全チャンクベクトルと比較
3. 類似度が高いチャンクを取得（Top 3-5件）
4. 該当チャンクをLLMに渡して回答生成

【結果】
ドキュメント内の「犬」「ペット」「動物」などの
関連セクションを自動的に見つけて回答
```

---

## Docker構成

### Dockerfile

```dockerfile
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
```

### compose.yaml

```yaml
version: '3.8'

services:
  doc-sage:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: doc-sage-app
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CHROMA_PERSIST_DIRECTORY=/app/data/vectorstore
      - DB_PATH=/app/data/doc-sage.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./src:/app/src
    restart: unless-stopped
    networks:
      - doc-sage-network

networks:
  doc-sage-network:
    driver: bridge
```

---

## 環境変数設定

### .env.example

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Chroma設定
CHROMA_PERSIST_DIRECTORY=/app/data/vectorstore

# Database設定
DB_PATH=/app/data/doc-sage.db

# ログレベル
LOG_LEVEL=INFO

# Embedding設定
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 開発ステップ

### Phase 1: 環境セットアップ（1日目）

- [x] リポジトリ作成
- [x] ディレクトリ構成作成
- [x] Docker環境構築
- [x] 環境変数設定
- [x] 依存関係インストール確認

### Phase 2: 基本機能実装（2-3日目）

#### 2.1 ドキュメント処理
- [ ] PDFローダー実装
- [ ] テキスト分割機能実装
- [ ] 埋め込み生成機能実装
- [ ] Chromaへの保存機能実装

#### 2.2 データベース
- [ ] SQLiteセットアップ
- [ ] テーブル作成
- [ ] CRUD操作実装

#### 2.3 QAチェーン
- [ ] LangChain QAチェーン実装
- [ ] 会話メモリ機能実装
- [ ] 検索・取得機能実装

### Phase 3: UI実装（4-5日目）

- [ ] Streamlit基本画面作成
- [ ] ファイルアップロード機能
- [ ] チャット画面実装
- [ ] 会話履歴表示
- [ ] エラーハンドリング

### Phase 4: 統合・テスト（6-7日目）

- [ ] 全機能の統合
- [ ] 単体テスト作成
- [ ] 統合テスト実行
- [ ] バグ修正

### Phase 5: ドキュメント・デプロイ（8日目）

- [ ] README作成
- [ ] 使い方ドキュメント作成
- [ ] Docker動作確認
- [ ] デプロイ手順確認

---

## 主要機能フロー

### 1. ドキュメントアップロードフロー

```
ユーザー操作
    ↓
1. PDFファイル選択・アップロード
    ↓
2. ファイル保存 (data/documents/)
    ↓
3. SQLiteにメタデータ記録
    ↓
4. PDFからテキスト抽出
    ↓
5. テキストをチャンクに分割
    ↓
6. 各チャンクをベクトル化
    ↓
7. Chromaに保存
    ↓
完了通知
```

### 2. 質問応答フロー

```
ユーザー質問入力
    ↓
1. 質問をベクトル化
    ↓
2. Chromaで類似チャンク検索
    ↓
3. Top-K チャンクを取得（K=3-5）
    ↓
4. 会話履歴を取得（メモリ）
    ↓
5. LLMに質問+チャンク+履歴を渡す
    ↓
6. 回答生成
    ↓
7. SQLiteに会話保存
    ↓
回答表示
```

---

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd doc-sage
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集してOpenAI API Keyを設定
```

### 3. Dockerで起動

```bash
# ビルド & 起動
docker compose up --build

# バックグラウンドで起動
docker compose up -d

# ログ確認
docker compose logs -f

# 停止
docker compose down
```

### 4. アクセス

```
ブラウザで http://localhost:8501 を開く
```

---

## 今後の拡張計画

### Phase 2（本番環境）

- FastAPI導入（バックエンドAPI化）
- PostgreSQL移行（SQLiteから）
- FAISS導入（Chromaから、パフォーマンス向上）
- ユーザー認証機能
- マルチテナント対応

### Phase 3（機能拡張）

- Wordファイル対応
- 動画ファイル対応（YouTube、ローカル動画）
- 音声ファイル対応（Whisper連携）
- マルチドキュメント横断検索
- 回答の引用元表示

---

## トラブルシューティング

### よくある問題

1. **OpenAI APIエラー**
   - `.env`ファイルのAPI Keyを確認
   - APIの利用制限・残高を確認

2. **Dockerボリュームの問題**
   ```bash
   # ボリュームをクリーンアップ
   docker compose down -v
   docker compose up --build
   ```

3. **ポート競合**
   - `compose.yaml`のポート番号を変更（例: 8502:8501）

4. **データが永続化されない**
   - `volumes`の設定を確認
   - `data/`ディレクトリの権限を確認

---

## 参考リンク

- [LangChain公式ドキュメント](https://python.langchain.com/)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [Chroma公式ドキュメント](https://docs.trychroma.com/)
- [Docker Compose仕様](https://docs.docker.com/compose/)

---

## ライセンス

MIT License

---

## 貢献

プルリクエスト歓迎！

---

**作成日:** 2025-10-01
**バージョン:** MVP v1.0