# NotebookLM Packet Prompt

This template is the human-side prompt used after manually uploading a packet bundle to NotebookLM. It does not drive any automated API call; DR-005 keeps NotebookLM automation out of scope.

## Upload checklist

Before sending this prompt, upload the following files from the packet directory (`data/packets/<packet_id>/`) as NotebookLM sources:

- `packet.md`
- `sources.json` (optional — useful when machine references are wanted)
- `timeline.md`
- `glossary.md`
- `questions.md`
- `operator_notes.md`

## Prompt body

```
あなたはネットニュース解説 YouTube チャンネルの編集補助です。

私は記事群を `packet.md` として渡しました。出力は最終台本ではなく、台本の素材です。

以下を順番に行ってください。

1. `packet.md` の primary_sources を一次情報、news_sources を二次情報として扱い、両者の差を要約してください。
2. `timeline.md` の時系列に矛盾や欠落があれば指摘してください。
3. `glossary.md` の各 term について 60 字以内の中立的な定義を提案してください。
4. `questions.md` の各問いについて、現時点で答えられること / 追加取材が必要なこと / 反対視点に分けて整理してください。
5. content_farm との重複を疑う場合、その兆候を理由とともに述べてください。
6. 出力は台本ではなく、台本の材料です。記事の文を 100 字以上連続で引用しないでください。
```

## Operator follow-up

NotebookLM の出力は `data/notebooklm/<packet_id>/raw_response.md` 程度に手で保存し、後工程の `newsroom script draft` (M4) で素材として読みます。NotebookLM の発話そのものをそのまま台本にしないでください。
