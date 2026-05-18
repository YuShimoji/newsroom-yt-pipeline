# Script Prompt — Yukkuri Dialogue

This prompt is used by an operator (or a future Gear-1 LLM step) to fill in TODO segments in a yukkuri-format ScriptIR. The drafter only produces the structure; the conversation between 霊夢 and 魔理沙 belongs here.

## Inputs

- `script.md` — chapter outline plus TODO placeholders per segment.
- `script_ir.json` — machine-readable speaker, claim_type, source_refs.
- `script_review.md` — guard findings to satisfy before approval.
- Packet bundle (`packet.md`, etc.) for source context.

## Prompt body

```
あなたは「ゆっくり解説」形式の YouTube 動画台本作家です。
霊夢 (聞き役・素朴な質問) と 魔理沙 (解説役・俯瞰視点) の 2 名で対話を書きます。

ルール:
1. 各 segment の claim_type を尊重する。
   - fact: source_refs にある一次情報のみを根拠にする。
   - interpretation: 「私はこう読んだ」「これは X を示唆する」という独自分析として書く。
   - speculation: 「まだ確証はないが」と明示する。
   - instruction: 視聴者への呼びかけ・問いかけ。
2. 記事タイトルをそのまま口述しない。事実関係は自分の言葉で再構成する。
3. 1 segment あたり 60-120 字を目安にする。
4. 章ごとの intent を逸脱しない。
5. 反対視点や批判視点を conflict 章に必ず入れる。
6. 視聴者の判断・行動・選択にどう関わるかを impact 章で具体化する。
```

## Operator notes

- 出力は `script.md` の各 segment に上書きで埋める。
- 埋めた後は `newsroom script critique --script <id>` を再実行する。
- 反対視点が packet に無い場合、operator が一次情報を追加してから書く。
