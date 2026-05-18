# プロジェクト仕様書: newsroom-yt-pipeline

作成日: 2026-05-16

この文書は、会話ログを実装可能なプロジェクト仕様へ再編したものです。新規リポジトリ `newsroom-yt-pipeline` の一次仕様として扱う想定です。

## 1. 結論

このプロジェクトは新規リポジトリで開始します。

既存の `NLMYTGen` は、NotebookLM 出力を YMM4 向け CSV / 演出 IR へ渡す下流アダプタとして温存します。ニュース収集、トピック選定、シリーズ戦略、引用・素材管理、チャンネル運営判断を `NLMYTGen` に入れません。

理由:

- `NLMYTGen` は公開 README 上でも NotebookLM 出力から YMM4 台本・演出補助へ向かう下流変換器として定義されています。
- 同 README では YouTube 連携、素材自動取得、サムネイル生成、自前 TTS、`.ymmp` ゼロ生成などが非目的として整理されています。
- 今回必要なのは、動画変換器ではなく、ニュース編集・企画・権利管理・シリーズ運用を含む上流の編集パイプラインです。

推奨名:

- 第一候補: `newsroom-yt-pipeline`
- 代替: `netnews-editorial-os`
- 代替: `yt-news-pipeline`

## 2. プロジェクト定義

`newsroom-yt-pipeline` は、毎日のネットニュースを、独自の文脈・分析・シリーズ性を持つ YouTube 解説動画へ変換するための半自動制作パイプラインです。

これは「ニュース記事読み上げ自動化」ではありません。動画化する対象は記事そのものではなく、記事群から抽出した問い、変化、対立、背景、視聴者にとっての判断材料です。

例:

```text
弱い題材:
Microsoft Copilot に新機能が追加されました

強い題材:
Copilot は社内情報の検索窓をどう変えるのか
Copilot は本当に日常業務で使えるのか
Copilot の権限管理はどこが危ないのか
```

差別化軸は速報性ではなく、文脈保持能力です。

## 3. 目的

本プロジェクトは以下を実現します。

- RSS / Inoreader / 公式発表 / 競合観測からニュース候補を集める。
- 記事を単体で扱わず、同一話題・同一文脈・同一シリーズ候補へ束ねる。
- まとめサイトや量産型ニュースサイトとの重複を検出する。
- 独自性、継続性、視覚化可能性、出典強度、著作権リスクで候補をスコアリングする。
- NotebookLM に投入する資料束を自動生成する。
- NotebookLM 出力を最終台本ではなく、台本素材・論点抽出・会話リズム参照として扱う。
- ゆっくり解説型、または青山龍星ナレーション型の台本を生成・検査する。
- 画像・スクリーンショット・引用候補を `AssetManifest` / `QuoteManifest` に記録する。
- 外部素材依存ではなく、独自カード、図解、時系列、比較表、リスク表示で視覚的情報量を増やす。
- YMM4 へ渡す CSV、演出メモ、素材・引用マニフェストを出力する。

## 4. 非目的

初期 MVP に含めないもの:

- YouTube 自動投稿。
- NotebookLM API 前提の自動操作。
- 画像・スクリーンショットの無審査自動利用。
- ニュース記事本文の長文転載。
- NotebookLM 出力の無検査採用。
- 完全な `.ymmp` ゼロ生成。
- 自前 TTS 実装。
- サムネイル自動生成。
- GUI / ダッシュボード。
- 法的判断の自動確定。
- 広範なクローラー。

## 5. システム全体像

```text
[1] Source Ingest
    RSS / Inoreader / 公式発表 / 競合観測

[2] Article Store
    URL、タイトル、媒体、公開日時、本文、取得状態、出典種別を保存

[3] Story Clustering
    複数記事を同一話題・同一文脈・同一シリーズ候補に束ねる

[4] Topic Scoring
    独自性、継続性、視覚化可能性、出典強度、著作権リスクを点数化

[5] NotebookLM Packet Builder
    NotebookLM に投入する資料束を Markdown / JSON で出力

[6] Script Workbench
    Packet / NotebookLM 出力を台本、構成、反証、補足情報へ変換

[7] Visual and Rights Planner
    VisualIR、AssetManifest、QuoteManifest、出典一覧、承認状態を管理

[8] YMM4 Package Export
    NLMYTGen adapter 経由で YMM4 CSV と編集ハンドオフ一式を出力
```

## 6. 責務境界

### 6.1 `newsroom-yt-pipeline` の責務

- RSS / Inoreader 設定。
- 記事取得。
- 記事 DB。
- 重複排除。
- 話題クラスタリング。
- 競合重複検出。
- トピックスコアリング。
- シリーズ管理。
- チャンネルメモリ。
- NotebookLM Packet 作成。
- 台本ドラフトと台本検査。
- VisualIR 作成。
- AssetManifest / QuoteManifest 作成。
- YMM4 export の上流パッケージング。

### 6.2 `NLMYTGen` の責務

- NotebookLM 由来テキストの整形。
- YMM4 台本 CSV 生成。
- YMM4 向け演出 IR / patch 支援。
- 既存の YMM4 変換・検査機能。

### 6.3 統合方式

次のいずれかで統合します。

- subprocess 呼び出し。
- ローカル path dependency。
- pip dependency。
- JSON / CSV / Markdown の schema 境界。

共有 GUI コード化はしません。

## 7. 外部仕様の確認メモ

2026-05-16 時点で公式情報を確認した制約です。実装前に再確認が必要です。

### 7.1 Inoreader

設計上の扱い:

- 任意の高機能取材デスク。
- MVP は通常 RSS から開始し、Inoreader は後続または stub から開始。

確認事項:

- Inoreader API は OAuth 2.0 を使います。
- API 利用は公開アプリ開発者向けで、それ以外の用途は Pro plan が必要と説明されています。
- `stream/contents` は JSON で記事を返します。
- `stream/contents` は Zone 1 に属します。
- デフォルト API 制限は Zone 1 / Zone 2 ともに 100 requests/day です。

設計要件:

- 差分取得を基本にする。
- 連続ポーリングしない。
- rate-limit header を保存する。
- 最終取得時刻 / cursor を保存する。
- API が使えない環境でも RSS MVP が動くようにする。

公式参照:

- <https://www.inoreader.com/developers/>
- <https://www.inoreader.com/developers/oauth>
- <https://www.inoreader.com/developers/stream-contents>
- <https://www.inoreader.com/developers/rate-limiting>

### 7.2 NotebookLM

設計上の扱い:

- 最終台本製造機ではなく、資料圧縮器・論点抽出器。
- MVP では手動投入前提。

確認事項:

- 利用上限はプラン依存かつ変更され得ます。
- 基本枠として 100 notebooks/user、50 sources/notebook、50 chats/day、3 audio overviews/day が掲載されています。
- 日次 quota は 24 時間、月次 quota は 30 日で reset と説明されています。
- Enterprise / Google Cloud 経由の利用は後期検討です。

設計要件:

- Packet をローカル成果物として保存する。
- NotebookLM UI/API に依存しない。
- Packet は一次情報、主要報道、批判的視点、時系列、用語集、質問に分ける。

公式参照:

- <https://support.google.com/notebooklm/answer/16213268>

### 7.3 YMM4

設計上の扱い:

- 最終編集盤面。
- 自動化対象は YMM4 に入れる前の CSV、VisualIR、素材・引用メモまで。

確認事項:

- YMM4 は `ツール -> 台本読み込み` から台本編集ウィンドウを扱えます。
- TXT 台本は `キャラクター名「セリフ内容」` 形式。
- CSV 台本は `キャラクター名,セリフ内容` 形式。
- 行頭 `#` はコメントとして扱えます。
- CSV 内のカンマ・改行は quote が必要です。

設計要件:

- CSV は Python の csv writer で生成する。
- デフォルトはヘッダーなし 2 列。
- speaker mapping を config で持つ。
- `ymm4_notes.md` を必ず同梱する。

公式参照:

- <https://manjubox.net/ymm4/faq/editing/%E5%8F%B0%E6%9C%AC%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E3%82%82%E3%81%A8%E3%81%AB%E3%83%9C%E3%82%A4%E3%82%B9%E3%82%A2%E3%82%A4%E3%83%86%E3%83%A0%E3%82%92%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B/>

### 7.4 VOICEVOX / 青山龍星

設計上の扱い:

- 表記は `青山龍星`。
- 利用規約確認とクレジットをパイプライン上の承認項目にする。

確認事項:

- VOICEVOX 公式は青山龍星を無料テキスト読み上げソフトとして掲載しています。
- 商用・非商用問わず無料としつつ、各キャラクター利用規約確認が必要とされています。
- VirVox Project 規約ではクレジット表記が必要です。
- `VOICEVOX青山龍星` については、企業・個人事業主・企業等と契約した個人が作品を公開する場合、収益の有無にかかわらず `ななはぴ` への事前申請が必要とされています。

設計要件:

- `voice_terms_status` を episode 単位で持つ。
- `credit_text` を出力する。
- 公開前の human approval を必須にする。

公式参照:

- <https://voicevox.hiroshiba.jp/product/aoyama_ryusei/>
- <https://www.virvoxproject.com/voicevox%E3%81%AE%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84>

### 7.5 YouTube 収益化 / reused content

設計上の扱い:

- 著作権とは別に、YouTube 収益化上の reused content リスクも管理する。

確認事項:

- YouTube は独自性と視聴者への付加価値を求めています。
- 他者コンテンツに最小限の変更を加えただけでは reused content に該当し得ます。
- reused content は copyright enforcement とは別の判断です。

設計要件:

- Script Workbench で「記事読み上げ」「低変換」「独自コメント不足」を検出する。
- 外部画像・外部映像を主役にしない。
- 独自分析、比較、図解、構成を主にする。

公式参照:

- <https://support.google.com/youtube/answer/1311392>

### 7.6 引用・著作権

この仕様は法的助言ではありません。プロダクト上の安全制御です。

文化庁資料で整理されている引用条件として、以下を管理対象にします。

- 公表済み著作物であること。
- 引用の必然性があること。
- 引用部分が明確に区別されること。
- 報道、批評、研究など目的上正当な範囲であること。
- 主従関係が明確であること。
- 必要最小限度であること。
- 出所を明示すること。

設計要件:

- 画像・スクリーンショットは初期値 `human_required`。
- 引用理由、利用範囲、表示秒数、出所、改変内容、承認状態を manifest に残す。
- 引用が不要な場合は独自図解へ変換する。

公式参照:

- <https://www.bunka.go.jp/seisaku/chosakuken/textbook/pdf/94080901_01.pdf>

## 8. 初期シリーズ案

### 8.1 Copilot Watch

目的:

Microsoft Copilot を職場の情報インターフェースとして継続観測する。

候補回:

- Copilot とは何か。
- Copilot は本当に日常業務に使えるのか。
- Copilot のサイレント変更・機能差分を追う。
- Copilot が社外秘メールや社内文書をどう扱うか。
- Microsoft は Copilot をどう収益化したいのか。

### 8.2 Big Tech UI 政治学

目的:

UI 変更を企業戦略、広告、規制、囲い込み、ユーザー行動の観点から読む。

候補回:

- Google 検索結果はどう変わっているか。
- YouTube 収益化ポリシー変更は何を意味するか。
- X / Meta / TikTok の仕様変更は誰に得か。
- AI 機能は便利なのか、それとも囲い込みなのか。

### 8.3 サイレントナーフ観測所

目的:

告知されにくい劣化、制限、価格改定を追う。

候補:

- 無料枠縮小。
- 価格改定。
- API 制限。
- UI 劣化。
- 広告増加。
- 規約変更。

### 8.4 事件をプロダクト設計から読む

目的:

炎上や事故を個人のミスだけでなく、設計・運用・制度から分析する。

候補:

- 情報漏えいはなぜ起きたのか。
- 炎上はどの UI / 規約 / 運用で増幅したのか。
- セキュリティ事故は個人のミスか、設計の失敗か。

### 8.5 クリエイター経済ニュース

目的:

YouTube、AI生成コンテンツ、著作権、審査、収益化をクリエイター視点で扱う。

候補:

- YouTube 収益化ポリシー。
- AI 生成コンテンツ規制。
- 著作権と引用。
- プラットフォーム審査基準。
- 個人クリエイターの運用戦略。

## 9. トピックスコアリング

候補選定は話題性だけで行いません。

```text
topic_score =
  0.25 * update_potential
+ 0.20 * source_diversity
+ 0.15 * uniqueness
+ 0.15 * viewer_utility
+ 0.10 * visualizability
+ 0.10 * evidence_strength
- 0.15 * copyright_risk
- 0.10 * content_farm_overlap
```

指標:

| 指標 | 意味 |
| --- | --- |
| `update_potential` | 今後も続報・検証・差分が出るか |
| `source_diversity` | 公式、報道、批判、利用者視点が揃うか |
| `uniqueness` | まとめサイトと異なる問い・角度があるか |
| `viewer_utility` | 視聴者の判断や行動に役立つか |
| `visualizability` | 図解、比較、時系列にしやすいか |
| `evidence_strength` | 一次情報に近い根拠があるか |
| `copyright_risk` | 外部素材・本文引用依存が強すぎないか |
| `content_farm_overlap` | 量産型ニュースと丸被りしていないか |

競合サイトは避ける対象ではなく、重複を測るセンサーとして扱います。被った場合は捨てるだけでなく、問いを変えます。

## 10. 中核データモデル

### 10.1 Article

```yaml
id: string
url: string
canonical_url: string | null
title: string
source_name: string
source_url: string | null
author: string | null
published_at: datetime | null
fetched_at: datetime
body_text: string | null
summary: string | null
language: string | null
tags: list[string]
source_type: enum[official, news, commentary, competitor, social, unknown]
license_hint: string | null
hash_url: string
hash_title: string
hash_body: string | null
fetch_status: enum[pending, fetched, failed, skipped]
fetch_error: string | null
```

### 10.2 SourceFeed

```yaml
id: string
name: string
kind: enum[rss, inoreader_stream, manual]
url: string | null
inoreader_stream_id: string | null
source_type: enum[official, news, commentary, competitor, social, unknown]
tags: list[string]
enabled: bool
fetch_interval_minutes: int
last_fetched_at: datetime | null
last_cursor: string | null
```

### 10.3 StoryCluster

```yaml
id: string
title: string
summary: string
articles: list[string]
primary_sources: list[string]
related_series: list[string]
timeline: list[TimelineEvent]
entities: list[string]
content_farm_overlap: float
created_at: datetime
updated_at: datetime
```

### 10.4 NotebookPacket

```yaml
id: string
story_cluster_id: string
primary_sources: list[SourceRef]
news_sources: list[SourceRef]
critical_views: list[SourceRef]
timeline: list[TimelineEvent]
glossary: list[GlossaryTerm]
questions: list[string]
format_hint: enum[yukkuri, anchor, information_program]
export_dir: string
created_at: datetime
```

出力:

- `packet.md`
- `sources.json`
- `timeline.md`
- `glossary.md`
- `questions.md`
- `operator_notes.md`

### 10.5 EpisodePlan

```yaml
id: string
story_cluster_id: string
series_id: string | null
title_candidates: list[string]
thumbnail_angles: list[string]
hook: string
chapter_outline: list[Chapter]
target_duration_sec: int
viewer_utility: string
risk_notes: list[string]
approval_state: enum[draft, needs_review, approved, rejected]
```

### 10.6 ScriptIR

```yaml
id: string
episode_plan_id: string
format: enum[yukkuri_dialogue, anchor_narration]
segments:
  - id: string
    chapter_id: string
    speaker: string
    text: string
    source_refs: list[string]
    visual_refs: list[string]
    claim_type: enum[fact, interpretation, speculation, instruction]
    needs_human_review: bool
created_at: datetime
```

### 10.7 VisualIR

```yaml
id: string
script_id: string
visual_units:
  - id: string
    segment_refs: list[string]
    unit_type: enum[source_card, claim_evidence_card, timeline_spine, version_diff, actor_map, risk_meter, context_stack, takeaway_row, quote_screenshot, neutral_background]
    duration_sec: float
    layout_template: string
    source_refs: list[string]
    asset_refs: list[string]
    density_score: float
    approval_state: enum[auto_ok, human_required, approved, rejected]
```

### 10.8 AssetManifest

```yaml
episode_id: string
assets:
  - asset_id: string
    type: enum[screenshot, image, logo, chart, generated_diagram, local_template, other]
    source_url: string | null
    source_title: string | null
    author: string | null
    captured_at: datetime | null
    intended_use: string
    quote_reason: string | null
    display_duration_sec: float | null
    crop_ratio: string | null
    modification: string
    attribution_text: string | null
    risk_level: enum[low, medium, high]
    approval_state: enum[suggested, human_required, approved, rejected]
```

### 10.9 QuoteManifest

```yaml
episode_id: string
quotes:
  - quote_id: string
    source_ref: string
    quote_type: enum[text, screenshot, image, clip, data]
    purpose: enum[criticism, explanation, comparison, evidence, background]
    necessity: string
    quoted_scope: string
    main_subordinate_assessment: string
    distinction_method: string
    attribution: string
    risk_level: enum[low, medium, high]
    approval_state: enum[human_required, approved, rejected]
```

## 11. 設定ファイル

### 11.1 `configs/sources.yml`

```yaml
feeds:
  - id: microsoft_blog
    name: Microsoft Blog
    kind: rss
    url: https://example.com/feed.xml
    source_type: official
    tags: [watch/bigtech, series/copilot]
    enabled: true

  - id: competitor_itmedia
    name: ITmedia
    kind: rss
    url: https://example.com/rss
    source_type: competitor
    tags: [pool/competitor-watch]
    enabled: true

inoreader:
  enabled: false
  client_id_env: INOREADER_CLIENT_ID
  client_secret_env: INOREADER_CLIENT_SECRET
  token_store: data/secrets/inoreader_token.json
  streams:
    - id: ai_watch
      stream_id: user/-/label/watch-ai
      tags: [watch/ai]
```

### 11.2 `configs/series.yml`

```yaml
series:
  - id: copilot_watch
    title: Copilot Watch
    description: Microsoft Copilotを職場の情報インターフェースとして継続観測する。
    tags: [series/copilot, watch/bigtech]
    default_format: anchor
    strategic_question: Copilotは社内情報の流れをどう変えるのか。
```

### 11.3 `configs/autonomy.yml`

```yaml
autonomy:
  topic_selection: assist
  source_packet: auto
  script_generation: draft_only
  structure_design: approve
  visual_assets: suggest_only
  quote_policy: human_required
  voice_terms: human_required
  ymm4_export: auto_csv_manual_render
  publishing: manual
```

### 11.4 `configs/quote_policy.yml`

```yaml
quote_policy:
  default_image_approval: human_required
  default_text_quote_approval: human_required
  require_source_url: true
  require_quote_reason: true
  require_attribution: true
  prefer_original_diagram_when_possible: true
  max_unreviewed_external_assets: 0
```

## 12. CLI 仕様

CLI 名:

```bash
newsroom
```

### 12.1 取得・レポート

```bash
newsroom fetch --source rss
newsroom fetch --source inoreader
newsroom fetch --all
newsroom report --today
newsroom report --date 2026-05-16
```

MVP 要件:

- `configs/sources.yml` を読む。
- enabled な RSS を取得する。
- title / URL / source / published_at を正規化する。
- SQLite に保存する。
- canonical URL、URL hash、title/source で重複排除する。
- 日次候補表を出す。

### 12.2 クラスタリング・スコアリング

```bash
newsroom cluster --date today
newsroom score --date today
newsroom shortlist --date today --top 10
```

### 12.3 NotebookLM Packet

```bash
newsroom packet build --story story_20260516_001
newsroom packet export --packet packet_001 --format markdown
```

### 12.4 台本

```bash
newsroom script draft --format yukkuri --packet packet_001
newsroom script draft --format anchor --packet packet_001
newsroom script critique --script script_001
newsroom script revise --script script_001 --gear 2
```

台本検査項目:

- 事実主張に出典があるか。
- 推測と事実が分離されているか。
- 記事読み上げになっていないか。
- 独自分析が主、引用が従になっているか。
- 視聴者にとっての便益が明確か。
- 反対視点・批判視点があるか。
- 視覚更新ポイントが不足していないか。

### 12.5 Visual / Asset

```bash
newsroom visual plan --script script_001
newsroom asset suggest --story story_001
newsroom asset audit --episode episode_001
```

### 12.6 YMM4 Export

```bash
newsroom export ymm4 --script script_001 --adapter nlmytgen
```

出力:

```text
exports/episode_001/
  script.csv
  script_ir.json
  visual_plan.md
  visual_ir.json
  asset_manifest.yml
  quote_manifest.yml
  source_list.md
  ymm4_notes.md
```

### 12.7 週次戦略

```bash
newsroom strategy weekly
newsroom series report --series copilot_watch
```

## 13. 人間介入ギア

完全自動化を初期目標にしません。工程ごとに自動化粒度を切り替えます。

| 工程 | Gear 0 | Gear 1 | Gear 2 | Gear 3 |
| --- | --- | --- | --- | --- |
| ネタ選定 | 人間が選ぶ | AI が候補提示 | AI がスコアリング | AI が暫定 shortlist |
| ソース選定 | 人間が収集 | AI が候補提示 | AI が Packet 化 | 人間は除外中心 |
| 台本 | 人間が執筆 | NotebookLM/AI 下書き | AI が批評・修正 | 人間が最終監修 |
| 動画構成 | 人間が章立て | AI が章立て案 | AI が秒単位案 | 人間が差分確認 |
| 画像・引用 | 人間が選ぶ | AI が候補提示 | AI が引用理由生成 | 人間承認は残す |
| YMM4 | 手動 | CSV 自動 | CSV + notes + VisualIR | 書き出し前確認中心 |
| チャンネル編成 | 人間が企画 | AI が週次案 | AI がシリーズ更新案 | 人間が方針承認 |

常に human approval を残す工程:

- 引用。
- 外部画像・スクリーンショット。
- 名誉毀損・プライバシーに関わる主張。
- 青山龍星など音声ライブラリ規約。
- 最終台本。
- 公開。

## 14. VisualIR / 画面設計

外部画像を主役にしません。画面の主役は独自の情報構造です。

標準部品:

1. `source_card`: 出典、日時、媒体、主張をカード化。
2. `claim_evidence_card`: 主張と根拠を分離。
3. `timeline_spine`: 過去ニュースと今回の位置づけ。
4. `version_diff`: 規約、UI、料金、機能の差分。
5. `actor_map`: 企業、ユーザー、規制当局、競合の関係。
6. `risk_meter`: 著作権、プライバシー、炎上、規制、収益化リスク。
7. `context_stack`: 事件、背景、前回動画、今後の注目点。
8. `takeaway_row`: 視聴者が持ち帰る要点。

視覚密度:

- 8〜12 秒に 1 回、意味のある視覚更新を入れる。
- アニメーション量より可読性を優先する。
- 外部素材は証拠片であり、画面価値の中心ではない。

## 15. 推奨リポジトリ構成

```text
newsroom-yt-pipeline/
  README.md
  pyproject.toml
  configs/
    sources.yml
    series.yml
    autonomy.yml
    layouts.yml
    quote_policy.yml

  prompts/
    notebook_packet_prompt.md
    script_yukkuri_prompt.md
    script_anchor_prompt.md
    visual_plan_prompt.md
    title_thumbnail_prompt.md

  src/newsroom/
    __init__.py
    cli/
      main.py
    ingest/
      rss_client.py
      inoreader_client.py
      article_extractor.py
      source_registry.py
    store/
      models.py
      db.py
      migrations/
    clustering/
      story_clusterer.py
      similarity.py
    scoring/
      topic_scorer.py
      competitor_overlap.py
      evidence_score.py
    notebook/
      packet_builder.py
      packet_schema.py
      export_markdown.py
    editorial/
      series_graph.py
      episode_planner.py
      channel_memory.py
      weekly_strategy.py
    script/
      script_ir.py
      script_rewriter.py
      dialogue_formatter.py
      narration_formatter.py
    assets/
      asset_discovery.py
      asset_registry.py
      quote_manifest.py
      rights_checker.py
    layout/
      visual_ir.py
      visual_density.py
      card_templates.py
    adapters/
      nlmytgen_adapter.py
      ymm4_export.py
      notebooklm_manual_bridge.py

  data/
    articles/
    packets/
    scripts/
    manifests/
    exports/

  reports/
    daily/
    weekly/

  docs/
    PROJECT_SPEC.md
    AGENT_BRIEF.md
    architecture.md
    editorial_policy.md
    copyright_policy.md
    ymm4_workflow.md
```

## 16. 実装マイルストーン

### M1: RSS / Inoreader 収集 MVP

目的:

動画生成ではなく、記事台帳を作る。

成果物:

- Python project。
- 設定ファイル。
- SQLite DB。
- `Article` / `SourceFeed` model。
- RSS fetcher。
- Inoreader client stub。
- `newsroom fetch --source rss`。
- `newsroom report --today`。
- README。

完了条件:

- RSS を 1 つ以上取得できる。
- title / URL / source / published_at / fetched_at を保存できる。
- 同一 URL を重複保存しない。
- 日次候補一覧が読める。

### M2: Story Clustering / Topic Scoring

目的:

記事一覧を動画候補へ変換する。

成果物:

- `StoryCluster`。
- title/entity/source tag による初期 clustering。
- `TopicScore`。
- `newsroom cluster`。
- `newsroom score`。

### M3: Notebook Packet Builder

目的:

NotebookLM に渡す資料束を作る。

成果物:

- `NotebookPacket`。
- `packet.md`。
- `sources.json`。
- `timeline.md`。
- `glossary.md`。
- `questions.md`。

### M4: Script Workbench

目的:

NotebookLM 出力や Packet から台本 draft と検査結果を作る。

成果物:

- `EpisodePlan`。
- `ScriptIR`。
- `script.md`。
- `script_ir.json`。
- `script_review.md`。

### M5: YMM4 Export

目的:

YMM4 に投入できる最初の下流成果物を作る。

成果物:

- `NLMYTGenAdapter`。
- `YMM4Package`。
- `script.csv`。
- `ymm4_notes.md`。

### M6: VisualIR / AssetManifest / QuoteManifest

目的:

視覚設計と権利台帳を作る。

成果物:

- `VisualIR`。
- `AssetManifest`。
- `QuoteManifest`。
- `visual_plan.md`。

### M7: Series Planner

目的:

日次制作をチャンネル記憶へ接続する。

成果物:

- `SeriesGraph`。
- `ChannelMemory`。
- `weekly_strategy.md`。
- `series_graph.json`。

## 17. テスト方針

M1 の最小テスト:

- config load。
- RSS 正規化。
- published date 欠落時の処理。
- DB insert。
- URL 重複排除。
- `report --today` 出力。

M2 の最小テスト:

- 類似タイトルが cluster される。
- 無関係記事が cluster されない。
- score formula が deterministic。

M5 の最小テスト:

- CSV 内のカンマ、引用符、改行を正しく quote する。
- speaker mapping が config の YMM4 キャラクター名を使う。
- export directory に必要ファイルが揃う。

広い E2E 自動化は、記事台帳、Packet、export artifact が安定してから追加します。

## 18. 日次運用フロー

M5 以後の想定:

```text
1. newsroom fetch --all
2. newsroom cluster --date today
3. newsroom score --date today
4. newsroom report --today
5. 人間が shortlist から選ぶ
6. newsroom packet build --story <story_id>
7. 人間が NotebookLM に Packet を投入
8. newsroom script draft / critique
9. 人間が台本編集
10. newsroom visual plan / asset audit
11. 人間が引用・素材・音声規約を承認
12. newsroom export ymm4 --script <script_id> --adapter nlmytgen
13. 人間が YMM4 に読み込み、音声・演出を確認して書き出し
```

## 19. 初回 Agent への投入指示

```text
docs/PROJECT_SPEC.md を一次仕様として扱ってください。
まず M1 だけを実装してください。

実装対象:
- Python project 初期化
- 推奨ディレクトリ作成
- configs/sources.yml
- configs/series.yml
- configs/autonomy.yml
- configs/layouts.yml
- configs/quote_policy.yml
- Article / SourceFeed model
- SQLite persistence
- RSS fetcher
- Inoreader client stub
- newsroom fetch --source rss
- newsroom report --today
- README
- focused tests

まだ実装しないもの:
- NotebookLM API automation
- YMM4 export
- asset download
- YouTube upload
- GUI
- full .ymmp generation
```

## 20. 初期 MVP 完了条件

初期 MVP は以下を満たせば完了です。

- RSS feed 一覧を `configs/sources.yml` から読める。
- RSS から記事 title / URL / published_at / source を取得できる。
- 記事を SQLite に保存できる。
- 同一 URL を重複保存しない。
- `newsroom report --today` が候補一覧を出す。
- `TopicScorer` の雛形があり、仮 score の内訳を出せる。
- `NotebookPacket` の雛形、または M3 へ接続する interface がある。
- README に目的、非目的、MVP、次フェーズが書かれている。
- focused tests が通る。

## 21. 決定記録

### DR-001: 新規リポジトリ

決定:

新規 repo として開始する。

理由:

ニュース収集、企画、引用管理、素材承認、シリーズ戦略は `NLMYTGen` の責務ではない。`NLMYTGen` は YMM4 変換器として使う。

### DR-002: CLI 先行

決定:

GUI より CLI と file artifact を先に作る。

理由:

最初に固めるべきものは見た目ではなく、記事台帳、Packet、権利 manifest、YMM4 handoff であるため。

### DR-003: RSS 先行

決定:

Inoreader より通常 RSS MVP を先に実装する。

理由:

Inoreader は API 権限・OAuth・rate limit が絡む。RSS は初期台帳構築の最短経路。

### DR-004: 素材自動化より manifest 先行

決定:

画像ダウンロードより `AssetManifest` / `QuoteManifest` を先に作る。

理由:

リスクを下げるのは自動取得ではなく、利用目的、範囲、出典、承認状態の明示であるため。

### DR-005: NotebookLM は manual bridge 先行

決定:

NotebookLM API automation より、手動投入できる Packet を先に作る。

理由:

安定成果物は NotebookLM の UI 操作ではなく、資料束そのものだから。

### DR-006: NLMYTGen 統合は schema-only

決定日: 2026-05-18

決定:

`newsroom-yt-pipeline` と `NLMYTGen` の統合は CSV / Markdown / JSON の schema 境界のみで行う。subprocess 呼び出し、path dependency、pip dependency、共有コードは導入しない。

理由:

- newsroom 側の責務境界が明確になる。NLMYTGen の差し替えがコード変更を伴わない。
- プロセス起動失敗、依存衝突、path 解決のローカル差異など、統合特有の不安定さを排除する。
- NLMYTGen は YMM4 取り込みに閉じた変換器のままで、newsroom は YMM4 取り込み前段の素材生成に専念できる。

帰結:

- newsroom は `data/exports/episode_<id>/` に `script.csv` / `script_ir.json` / `source_list.md` / `ymm4_notes.md` / `export_manifest.json` を出力する。
- `export_manifest.json` は `story_cluster_id` / `episode_plan_id` / `script_id` / `packet_export_dir` への参照を保持し、上流の所在を追える形にする。
- NLMYTGen は newsroom の出力ディレクトリを入力として独立に処理する。逆方向の依存は持たない。
- M5 では subprocess / pip / path 結合は実装しない。必要になった時点で別 DR で再判断する。
