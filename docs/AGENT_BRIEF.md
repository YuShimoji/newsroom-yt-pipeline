# Agent Brief: newsroom-yt-pipeline

`docs/PROJECT_SPEC.md` を一次仕様として扱ってください。この文書は初回実装 Agent に渡す短い実行ブリーフです。

## 目的

ネットニュース特化 YouTube チャンネルのための半自動制作パイプラインを作ります。

これはニュース記事読み上げ自動化ではありません。ニュース記事群を、独自の問い、分析、シリーズ文脈、視覚構成を持つ動画企画へ変換する編集システムです。

## リポジトリ判断

新規 repo `newsroom-yt-pipeline` として作ります。

`NLMYTGen` は NotebookLM / YMM4 変換の下流アダプタとして扱います。ニュース収集、ソース戦略、権利管理、チャンネル編成、公開判断を `NLMYTGen` に入れないでください。

## 最初に実装する範囲: M1 のみ

実装対象:

1. Python project 初期化。
2. 推奨ディレクトリ構成。
3. 設定ファイル作成:
   - `configs/sources.yml`
   - `configs/series.yml`
   - `configs/autonomy.yml`
   - `configs/layouts.yml`
   - `configs/quote_policy.yml`
4. model:
   - `Article`
   - `SourceFeed`
5. SQLite persistence。
6. RSS fetcher。
7. Inoreader client stub。
8. CLI:
   - `newsroom fetch --source rss`
   - `newsroom report --today`
9. README。
10. focused tests:
   - config load
   - RSS normalization
   - DB deduplication
   - report output

## まだ実装しないもの

- NotebookLM API automation。
- YMM4 export。
- YouTube upload / publishing。
- 画像ダウンロード。
- 外部素材の自動利用。
- full `.ymmp` generation。
- GUI / dashboard。
- LLM による最終台本生成。
- 広範な crawler。

## 責務境界

`newsroom-yt-pipeline` が持つもの:

- Source ingest。
- Article ledger。
- Story clustering。
- Topic scoring。
- NotebookLM packet。
- Script workbench。
- VisualIR。
- AssetManifest。
- QuoteManifest。
- Series strategy。

`NLMYTGen` が持つもの:

- NotebookLM output normalization。
- YMM4 CSV conversion。
- 既存の YMM4 direction IR / patch support。

統合は subprocess、package dependency、local path dependency、または schema 境界で行ってください。

## Human approval を残すもの

- 引用。
- 外部画像 / screenshot。
- 音声ライブラリ規約。
- 名誉毀損・プライバシーに関わる主張。
- 最終台本。
- 公開。

## M1 完了条件

- `configs/sources.yml` から RSS feed を読める。
- RSS から title / URL / source / published_at / fetched_at を保存できる。
- 同一 URL を重複保存しない。
- `newsroom report --today` が候補一覧を出す。
- README が目的、scope、non-scope、次 milestone を説明している。
- focused tests が通る。

## 残作業の報告形式

残作業は以下を含めて報告してください。

- purpose
- effect
- requirements
- state
- owner
- next move
