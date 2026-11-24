"""주간 제작용: 질문글 댓글을 사람별 1개씩 모아 보여준다(순위 JSON을 만들 때 참고).
사용: python3 cardgen/show_replies.py 2026-12-02_1230"""
import json, sys
from pathlib import Path
d = json.loads((Path(__file__).resolve().parent.parent / "data" / "replies" / f"{sys.argv[1]}.json").read_text(encoding="utf-8"))
seen = {}
for r in d["replies"]:
    seen.setdefault(r["voter"], []).append(r["text"])
print(f"질문: {d['question'][:60]}…\n댓글 {len(d['replies'])}개, 참여자 {len(seen)}명\n")
for v, texts in seen.items():
    print("-", " / ".join(t.replace("\n", " ") for t in texts))
