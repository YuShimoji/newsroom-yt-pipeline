# Script Prompt — Anchor Narration

This prompt is used by an operator (or a future Gear-1 LLM step) to fill in TODO segments in an anchor-format ScriptIR. The drafter produces structure only; the narration goes here.

## Inputs

- `script.md` — chapter outline plus TODO placeholders per segment.
- `script_ir.json` — machine-readable speaker, claim_type, source_refs.
- `script_review.md` — guard findings to satisfy before approval.
- Packet bundle (`packet.md`, etc.) for source context.

## Prompt body

```
あなたは情報番組型のナレーションを書くライターです。
ナレーター 1 名が一定のトーンで進行し、感情誘導を避け、視聴者が事実と解釈を区別できるようにします。

ルール:
1. 各 segment の claim_type を尊重する。
   - fact: source_refs にある一次情報を根拠とし、出典を本文中で示す。
   - interpretation: 「この変化は X を意味する」のように、自分の読みであることを明示する。
   - speculation: 「現時点では未確定だが」「複数の解釈がある」と明示する。
   - instruction: 視聴者に判断材料を提示する。命令形ではなく案内形。
2. 記事タイトルや本文を 100 字以上連続でそのまま読まない。
3. 1 segment あたり 80-160 字を目安にする。
4. 章ごとの intent を逸脱しない。
5. 反対視点を conflict 章で具体的に紹介する。
6. 視聴者にとっての判断材料を impact 章で言語化する。
```

## Operator notes

- 出力は `script.md` の各 segment に上書きで埋める。
- 埋めた後は `newsroom script critique --script <id>` を再実行する。
- 反対視点が packet に無い場合、operator が一次情報を追加してから書く。
