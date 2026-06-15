# Agent Brief: newsroom-yt-pipeline

この文書は初回実装 Agent に渡した履歴ブリーフです。現在の作業では、`docs/PROJECT_SPEC.md` の決定記録、`docs/NLMYTGEN_BOUNDARY.md`、`docs/HANDOFF.md`、`docs/RUNTIME_STATE.md`、`docs/META_REVIEW_LEDGER.md`、および `docs/verification/` の最新監査記録を優先してください。

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

現在の後継境界では、NLMYTGen 側に残っていた RSS / OPML / Reader 価値は Newsroom の source management として扱います。OPML import、source list readback、sanitized source smoke、RSS fetch、read-only Inoreader fetch は Newsroom 側の責務です。Inoreader OAuth / token storage / unread-read sync / subscription mutation / background polling は引き続き非目的です。

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

統合は CSV / JSON / Markdown の schema 境界に限定します。subprocess、package dependency、local path dependency、共有コード化は、`docs/PROJECT_SPEC.md` の DR-006 により現在の方針から外します。

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

## 現在の報告の考え方

この初期ブリーフの英語ラベル列挙は、現在の完了報告テンプレートとして使いません。複数の選択肢や残作業がある場合は、実際の判断軸に合わせた比較表と、次に着手しやすい入口を自然文で示してください。
