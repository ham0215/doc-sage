# 📚 Doc Sage - ドキュメントの賢者

PDFドキュメントに対してAIで質問応答ができるチャットボットです。LangChainとStreamlitを使用した、使いやすく高性能なRAG（Retrieval-Augmented Generation）システムです。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## ✨ 特徴

- 🔍 **高精度検索**: ベクトル検索で関連情報を素早く発見
- 💬 **会話型AI**: 文脈を理解した自然な対話
- 📄 **参照元表示**: 回答の根拠となる箇所を明示
- 💾 **履歴保存**: 会話履歴を自動保存
- 🐳 **Docker対応**: 簡単セットアップ＆デプロイ
- 🎨 **モダンUI**: Streamlitによる直感的なインターフェース

## 🚀 クイックスタート

### 前提条件

- Docker & Docker Compose
- OpenAI APIキー

### 1. リポジトリのクローン

```bash
git clone https://github.com/ham0215/doc-sage.git
cd doc-sage
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、OpenAI APIキーを設定：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Dockerで起動

```bash
# ビルド & 起動
docker compose up --build

# バックグラウンドで起動
docker compose up -d
```

### 4. アクセス

ブラウザで http://localhost:8501 を開く

## 📖 使い方

1. **PDFアップロード**: サイドバーからPDFファイルをアップロード
2. **処理完了を待つ**: ドキュメントが自動的に処理されます（数秒〜数分）
3. **質問を入力**: チャット欄に質問を入力
4. **回答を確認**: AIがドキュメントの内容を基に回答を生成

### スクリーンショット

```
┌─────────────────────────────────────────────────────────────┐
│  📚 Doc Sage                                         [×]    │
│  ドキュメントの賢者 - PDFドキュメントに質問できるAIチャットボット │
├─────────────┬───────────────────────────────────────────────┤
│  サイドバー  │  メインチャット画面                             │
│             │                                                │
│ 📤 アップロード│  💬 チャット                                  │
│ [PDF選択]   │  ┌────────────────────────────────────────┐ │
│             │  │ User: この文書の要約を教えて          │ │
│ 📄 現在の    │  └────────────────────────────────────────┘ │
│ ドキュメント │  ┌────────────────────────────────────────┐ │
│ ファイル名   │  │ Assistant: この文書は...              │ │
│ ステータス   │  │ 📄 参照元を表示 ▼                     │ │
│ 日時        │  └────────────────────────────────────────┘ │
│             │  [質問を入力してください...]              │
│ 🗑️ クリア   │                                                │
└─────────────┴───────────────────────────────────────────────┘
```

## 🏗️ アーキテクチャ

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
│  - PyPDFLoader (PDF読み込み)           │
│  - RecursiveCharacterTextSplitter       │
│  - OpenAI Embeddings                    │
│  - Chroma (ベクトルストア)              │
│  - ConversationalRetrievalChain         │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│          Storage Layer                  │
│  - SQLite (会話履歴・ドキュメント管理)  │
│  - Chroma (ベクトルデータ永続化)        │
│  - File Storage (アップロードファイル)  │
└──────────────────────────────────────────┘
```

## 🛠️ 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **UI** | Streamlit 1.31.0 |
| **LLM** | OpenAI GPT-3.5/4 |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector DB** | Chroma 0.4.22 |
| **Database** | SQLite |
| **Framework** | LangChain 0.1.0 |
| **Container** | Docker |

## 📁 プロジェクト構成

```
doc-sage/
├── compose.yaml              # Docker Compose設定（本番）
├── compose.dev.yaml          # Docker Compose設定（開発）
├── Dockerfile                # Dockerイメージ定義
├── requirements.txt          # Python依存関係
├── .env.example              # 環境変数テンプレート
├── src/                      # ソースコード
│   ├── config.py             # 設定管理
│   ├── main.py               # エントリーポイント
│   ├── database/             # データベース層
│   │   ├── models.py         # SQLAlchemyモデル
│   │   ├── crud.py           # CRUD操作
│   │   └── init_db.py        # DB初期化
│   ├── loaders/              # ドキュメントローダー
│   │   ├── base_loader.py    # 共通インターフェース
│   │   └── pdf_loader.py     # PDF読み込み
│   ├── processing/           # 処理ロジック
│   │   ├── text_splitter.py  # テキスト分割
│   │   ├── embeddings.py     # 埋め込み生成
│   │   └── vectorstore.py    # ベクトルストア管理
│   ├── chains/               # LangChainチェーン
│   │   ├── qa_chain.py       # QAチェーン
│   │   └── memory.py         # 会話メモリ
│   └── ui/                   # ユーザーインターフェース
│       └── app.py            # Streamlitアプリ
├── data/                     # データ保存（gitignore）
│   ├── documents/            # アップロードファイル
│   ├── vectorstore/          # Chromaデータ
│   └── doc-sage.db           # SQLiteデータベース
└── docs/                     # ドキュメント
    └── requirement.md        # 要件定義
```

## ⚙️ 設定

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `OPENAI_API_KEY` | OpenAI APIキー（必須） | - |
| `EMBEDDING_MODEL` | 埋め込みモデル | text-embedding-3-small |
| `CHUNK_SIZE` | テキストチャンクサイズ | 1000 |
| `CHUNK_OVERLAP` | チャンクオーバーラップ | 200 |
| `CHROMA_PERSIST_DIRECTORY` | Chroma永続化ディレクトリ | /app/data/vectorstore |
| `DB_PATH` | SQLiteデータベースパス | /app/data/doc-sage.db |
| `LOG_LEVEL` | ログレベル | INFO |

### 開発環境

開発モード（ホットリロード有効）で起動：

```bash
docker compose -f compose.dev.yaml up
```

## 🐛 トラブルシューティング

### OpenAI APIエラー

- `.env`ファイルのAPI Keyを確認
- APIの利用制限・残高を確認

### Dockerボリュームの問題

```bash
# ボリュームをクリーンアップ
docker compose down -v
docker compose up --build
```

### ポート競合

`compose.yaml`のポート番号を変更（例: 8502:8501）

### データが永続化されない

- `volumes`の設定を確認
- `data/`ディレクトリの権限を確認

## 🔄 今後の拡張予定

- [ ] Wordファイル対応
- [ ] 動画ファイル対応（YouTube、ローカル動画）
- [ ] 音声ファイル対応（Whisper連携）
- [ ] マルチドキュメント横断検索
- [ ] 回答の引用元表示強化
- [ ] ユーザー認証機能
- [ ] FastAPI化（バックエンドAPI分離）

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエスト歓迎！バグ報告や機能提案は[Issues](https://github.com/ham0215/doc-sage/issues)までお願いします。

## 📚 参考リンク

- [LangChain公式ドキュメント](https://python.langchain.com/)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [Chroma公式ドキュメント](https://docs.trychroma.com/)
- [OpenAI API](https://platform.openai.com/docs/)

---

**作成日:** 2025-10-01
**バージョン:** MVP v1.0
