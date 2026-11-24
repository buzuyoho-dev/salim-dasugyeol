"""최근 14일 내 질문글의 댓글을 모아 data/replies/<게시일>_<slot>.json 에 저장(다수결 원료).
아이디는 저장하지 않는다(공개 인용 시 개인 식별 방지). 중복 투표 방지용으로 아이디 해시만 남긴다."""
import datetime as dt, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import threads_api

ROOT = Path(__file__).resolve().parent.parent
KST = dt.timezone(dt.timedelta(hours=9))


def main():
    cutoff = dt.datetime.now(KST) - dt.timedelta(days=14)
    for res in (ROOT / "published").glob("*/*/result.json"):
        post = json.loads((res.parent / "post.json").read_text(encoding="utf-8"))
        if post.get("type") not in ("question", "vs"):
            continue
        r = json.loads(res.read_text(encoding="utf-8"))
        if dt.datetime.fromisoformat(r["posted_at"]) < cutoff:
            continue
        rows = []
        for c in threads_api.replies(r["id"]):
            if c.get("root_post", {}).get("id") not in (None, r["id"]):
                continue
            uid = hashlib.sha256((c.get("username") or "").encode()).hexdigest()[:12]
            rows.append({"voter": uid, "text": c.get("text", ""), "at": c.get("timestamp")})
        out = ROOT / "data" / "replies" / f"{res.parent.parent.name}_{res.parent.name}.json"
        out.write_text(json.dumps({"question": post["text"], "post_id": r["id"], "replies": rows},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{out.name}: 댓글 {len(rows)}개")


if __name__ == "__main__":
    main()
