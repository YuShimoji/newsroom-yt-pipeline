# NLMYTGen Boundary

`newsroom-yt-pipeline` と `NLMYTGen` の接続境界を固定する文書。

この文書は `docs/PROJECT_SPEC.md` の責務分離を運用時に見失わないための補助正本であり、Newsroom を NLMYTGen のサブディレクトリや共有ライブラリとして扱うためのものではない。

## 位置づけ

| Repo | 位置 | 持つ責務 |
| --- | --- | --- |
| `newsroom-yt-pipeline` | upstream editorial pipeline | source ingest, article ledger, story clustering, topic scoring, NotebookLM packet, script workbench, VisualIR, AssetManifest, QuoteManifest, channel memory |
| `NLMYTGen` | downstream adapter | NotebookLM output normalization, YMM4 CSV conversion, YMM4 direction IR / patch support, YMM4-facing review / proof ingest |

Newsroom は動画企画と編集パッケージを作る。NLMYTGen は、渡された packet / script / IR / manifest を YMM4 制作導線へ接続する。

RSS / OPML / Reader intake の後継は Newsroom 側である。NLMYTGen 側に残っていた `fetch-topics` / `list-feed-sources` / `rss-smoke` 系の価値は、Newsroom では `source import-opml`、`source smoke`、`fetch --source rss`、`fetch --source inoreader` の upstream source-management として扱う。

## 渡せる artifact

NLMYTGen へ渡す単位は、portable な export bundle に限定する。

| Artifact | 役割 |
| --- | --- |
| `export_manifest.json` | episode / story / script / packet / artifact path の索引 |
| `script.csv` | YMM4 台本読み込み候補 |
| `script_ir.json` | NLMYTGen 側 adapter / review の入力候補 |
| `visual_ir.json` | YMM4-facing visual planning の入力候補 |
| `visual_plan.md` | human-readable visual handoff |
| `source_list.md` | NLMYTGen 側が出典を確認するための一覧 |
| `asset_manifest.yml` | 素材候補と利用段階の管理 |
| `quote_manifest.yml` | 引用候補と承認状態の管理 |
| `ymm4_notes.md` | speaker mapping、warnings、human-required notes |

NLMYTGen 側で intake を始める前に、人間が copy-in か read-only path reference かを決める。

## 禁止する結合

次の結合は採用しない。

- Newsroom から NLMYTGen の Python module を import する。
- NLMYTGen から Newsroom の subprocess を呼ぶ。
- ローカル絶対パスを前提にした package / path dependency を作る。
- 共通コード化を理由に、YMM4 adapter 実装を Newsroom 側へ移す。
- Newsroom export が NLMYTGen repo に直接書き込む。
- runtime DB、proof screenshot、raw article body、private data、copyright-unclear text を handoff artifact として混ぜる。
- Newsroom 側で YMM4 geometry、render、publishing、`.ymmp` generation、NLMYTGen patch 実装を所有する。

## RSS / Reader 後継仕様

| 旧RSS/Reader価値 | Newsroomでの置き場 | 扱い |
| --- | --- | --- |
| OPML購読一覧の取り込み | `newsroom source import-opml --opml <path>` | raw OPML は repo 外。出力された reviewed YAML だけを人間確認後に採用する |
| AI側が見るsource一覧のreadback | `newsroom source list` | `configs/sources.yml` と `configs/source_pools.yml` の結果を読む |
| sanitized live smoke | `newsroom source smoke` | source数、category数、fetch状態、代表field有無だけを出し、記事タイトルやURLを evidence に出さない |
| RSS/Atom取得 | `newsroom fetch --source rss` | SQLite article ledger に保存し、cluster / score / packet へ接続する |
| Inoreader read-only取得 | `newsroom fetch --source inoreader` / `newsroom source smoke --source inoreader` | OAuth/token storage は未実装。`NEWSROOM_INOREADER_ACCESS_TOKEN` の一時tokenだけを環境変数で読む |

NLMYTGen側のRSS/Readerコードは互換参照として残っていても、active development はNewsroom側へ寄せる。NLMYTGen側へ戻すのは、Newsroom export bundle を受けた downstream adapter mapping だけである。

## Handoff readiness

NLMYTGen へ渡せる状態とは、次が読める状態である。

| 確認 | 条件 |
| --- | --- |
| manifest | episode / story / script / packet ID と artifact path が揃っている |
| script | CSV と ScriptIR の関係が説明できる |
| visual | VisualIR と visual plan が同じ構成を指している |
| source / rights | source list, asset manifest, quote manifest があり、未承認や deferred が明示されている |
| privacy / copyright | raw article body、private data、copyright-unclear copied text が含まれていない |
| NLMYTGen decision | copy-in / read-only reference と、最初の intake 形状が人間により選ばれている |

## Export 変更時の扱い

Newsroom 側で export bundle の field や artifact を増やす場合、まずこの境界文書と `docs/PROJECT_SPEC.md` の責務分離に合うか確認する。

NLMYTGen 側の implementation 変更は、Newsroom repo から直接行わない。必要な場合は NLMYTGen 側で `manifest-to-adapter mapping`、`docs-only intake plan`、または `adapter implementation slice` として別に起動する。

## 認識合わせ prompt

Newsroom レーンへ作業を渡すときは、NLMYTGen 側の `docs/LANE_ALIGNMENT_PROMPTS.md` の `newsroom-yt-pipeline レーン` を使う。
