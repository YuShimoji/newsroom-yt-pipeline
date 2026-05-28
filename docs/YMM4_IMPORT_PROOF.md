# YMM4 Import Proof

## 目的

`newsroom export ymm4` が生成した episode export bundle を、operator が手動で YMM4 に読み込み、YMM4 側で受理されることを証跡として残すための手順です。

この手順は YMM4 GUI automation ではありません。YMM4 の操作、画面確認、スクリーンショット取得、proof 記入は operator が手動で行います。

## 前提

- repo: `C:\Users\PLANNER007\newsroom-yt-pipeline`
- 一次仕様: `C:\Users\PLANNER007\newsroom-yt-pipeline\docs\PROJECT_SPEC.md`
- 現在地の正本: `C:\Users\PLANNER007\newsroom-yt-pipeline\docs\RUNTIME_STATE.md`
- `newsroom export ymm4` により episode export bundle が作成済みであること。
- bundle は M6.4 schema v2 の `export_manifest.json` を含むこと。
- `human_required` は公開前確認の安全ゲートであり、proof のために消してはいけません。

## 対象 Export Bundle の場所

標準の出力先は次です。

```text
C:\Users\PLANNER007\newsroom-yt-pipeline\data\exports\episode_<id>
```

別の `--export-root` を使った場合は、その配下の `episode_<id>` ディレクトリを対象にします。以後、このディレクトリを `<episode_dir>` と書きます。

## Import 前 Self-Check

YMM4 を開く前に、bundle の機械的な整合性を確認します。

```powershell
cd C:\Users\PLANNER007\newsroom-yt-pipeline
.venv\Scripts\Activate.ps1
newsroom export inspect --episode-dir <episode_dir>
```

この self-check は YMM4 GUI import の代替ではありません。必須ファイル、`export_manifest.json`、CSV/YAML の読み取り、manifest と実ファイルの一致、`human_required` の残存 warning を確認するための事前検査です。

## YMM4 で Script CSV を読み込む手順

1. YMM4 を起動します。
2. 対象 bundle の `<episode_dir>\script.csv` を確認します。
3. YMM4 の `ツール > 台本読み込み` を開きます。
4. `script.csv` を選択して読み込みます。
5. 読み込み後、台本編集ウィンドウまたはタイムライン上で各行の speaker と text を確認します。
6. 確認結果を proof template に記録します。
7. 必要に応じて YMM4 画面のスクリーンショットを保存し、proof の `evidence.screenshot_path` に記録します。

## 確認項目

| 確認すること | 見る場所 |
| --- | --- |
| `script.csv` が YMM4 の台本読み込みで受理される | YMM4 の読み込み結果 |
| speaker 名が期待通り扱われる: `霊夢` / `魔理沙` / `ナレーター` | YMM4 の話者名、キャラクター/音声割当 |
| `# Chapter: ...` コメント行が無害に扱われる | YMM4 上で余計なセリフにならないか |
| カンマを含むセリフが崩れない | `script.csv` の該当セリフと YMM4 上の表示 |
| 改行を含むセリフが崩れない | `script.csv` の該当セリフと YMM4 上の表示 |
| 日本語が文字化けしない | YMM4 上の各セリフ |
| `ymm4_notes.md` を見れば operator が次に何を確認すべきか分かる | `<episode_dir>\ymm4_notes.md` |
| `source_list.md` / `asset_manifest.yml` / `quote_manifest.yml` が bundle 内で見つかる | `<episode_dir>` |
| `export_manifest.json` の `artifacts` と実ファイルが一致する | `<episode_dir>\export_manifest.json` とファイル一覧 |
| `human_required` が残る asset / quote / visual は公開前に operator 確認が必要である | `visual_ir.json` / `asset_manifest.yml` / `quote_manifest.yml` |

## 合格条件

- YMM4 が `script.csv` をエラーなく受理する。
- speaker 名が YMM4 側で確認でき、必要なキャラクター/音声割当の差分が分かる。
- コメント行、カンマ、改行、日本語が、編集不能な崩れ方をしていない。
- `export_manifest.json` の `schema_version` が `2` で、`artifacts` が実ファイルと一致している。
- `ymm4_notes.md`、`source_list.md`、`asset_manifest.yml`、`quote_manifest.yml` が operator の確認に使える。
- `human_required` が残る場合、その確認が公開前作業として proof に記録されている。

## 失敗時に見るべき箇所

| 症状 | まず見る場所 | 次の動き |
| --- | --- | --- |
| `script.csv` を読み込めない | `<episode_dir>\script.csv` / `newsroom export inspect` の出力 | CSV の行構造、文字コード、コメント行を確認する |
| speaker が意図通り扱われない | `<episode_dir>\script.csv` / `C:\Users\PLANNER007\newsroom-yt-pipeline\configs\speakers.yml` | YMM4 側のキャラクター名と config の対応を確認する |
| カンマや改行が崩れる | `<episode_dir>\script.csv` | Python csv writer の quote 結果と YMM4 の解釈差を記録する |
| 日本語が文字化けする | `<episode_dir>\script.csv` / YMM4 import 設定 | UTF-8 CSV の読み込み可否を記録する |
| bundle 内のファイルが足りない | `<episode_dir>\export_manifest.json` / `newsroom export inspect` の出力 | `newsroom export ymm4 --script <script_id>` を再実行する |
| `human_required` が多い | `<episode_dir>\asset_manifest.yml` / `<episode_dir>\quote_manifest.yml` | 公開前確認として承認、却下、差し替えを proof に残す |

## 証跡の残し方

1. `C:\Users\PLANNER007\newsroom-yt-pipeline\docs\templates\ymm4_import_proof_template.yml` を proof の出発点にします。
2. runtime の proof は git 管理外の作業場所に保存します。推奨先は次です。

```text
C:\Users\PLANNER007\newsroom-yt-pipeline\data\proofs\ymm4_import\<episode_id>\proof.yml
```

3. YMM4 のスクリーンショットを残す場合は、同じ proof ディレクトリに保存し、`evidence.screenshot_path` に絶対パスまたは `<episode_dir>` からの明確なパスを記録します。
4. `import_result` と各 `checks` を `pass` / `fail` / `not_applicable` のいずれかへ更新します。
5. 問題がある場合は `issues` に再現手順、見たファイル、operator 判断を短く残します。
6. 最後に `decision.status` を `passed` / `blocked` / `needs_fix` のいずれかへ更新し、`decision.next_action` に次の動きを書きます。

## Proof Template の使い方

template は次にあります。

```text
C:\Users\PLANNER007\newsroom-yt-pipeline\docs\templates\ymm4_import_proof_template.yml
```

`repo_head` には `git rev-parse --short HEAD` の結果、`export_bundle` には `<episode_dir>`、`script_csv` には `<episode_dir>\script.csv`、`ymm4_version` には YMM4 のバージョン表記を記録します。

`warnings_observed` は `export_manifest.json` と `newsroom export inspect` の warning を見ながら埋めます。`critical_views_missing`、`speculation_vs_fact`、`needs_human_review`、`human_required_assets`、`human_required_quotes` は、proof の失敗理由とは限りません。公開前に確認すべき安全ゲートとして残します。
