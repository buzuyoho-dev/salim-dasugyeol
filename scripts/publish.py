"""queue/<YYYY-MM-DD>/<HHMM>/post.json 중 시간이 된 것을 게시하고 published/로 옮긴다.

post.json 예시
{"type": "question" | "vs" | "curation",
 "text": "본문",
 "images": ["cards/2026-12-16/1.jpg"],           # 저장소 안 경로(공개 raw 주소로 변환)
 "reply": {"text": "링크 + 공정위 문구"}}          # 선택
"""
import datetime as dt, json, os, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check, threads_api

ROOT = Path(__file__).resolve().parent.parent
KST = dt.timezone(dt.timedelta(hours=9))
MAX_PER_DAY = 3
RAW = "https://raw.githubusercontent.com/{repo}/main/{path}"


def due_items(now):
    items = []
    for f in sorted((ROOT / "queue").glob("*/*/post.json")):
        day, slot = f.parent.parent.name, f.parent.name
        when = dt.datetime.strptime(day + slot, "%Y-%m-%d%H%M").replace(tzinfo=KST)
        if when <= now:
            items.append((when, f))
    return items


def posted_today(now):
    d = ROOT / "published" / now.strftime("%Y-%m-%d")
    return len(list(d.glob("*/result.json"))) if d.exists() else 0


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    now = dt.datetime.now(KST)
    repo = os.environ.get("GITHUB_REPOSITORY", "buzuyoho-dev/salim-dasugyeol")
    failed = False
    for when, f in due_items(now):
        post = json.loads(f.read_text(encoding="utf-8"))
        bad = check.problems(post)
        if (now - when).total_seconds() > 6 * 3600:
            bad.append("예정 시각에서 6시간 넘게 지남(늦은 게시 방지)")
        if posted_today(now) >= MAX_PER_DAY:
            bad.append(f"오늘 이미 {MAX_PER_DAY}개 게시")
        if bad:
            print(f"[차단] {f.parent}: " + " / ".join(bad))
            hold = ROOT / "held" / f.parent.parent.name / f.parent.name
            if not dry:
                hold.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f.parent), hold)
                (hold / "reason.txt").write_text("\n".join(bad), encoding="utf-8")
            failed = True
            continue
        urls = [RAW.format(repo=repo, path=p) for p in post.get("images", [])]
        if dry:
            print(f"[시험] {f.parent} 통과, 이미지 {len(urls)}장")
            continue
        pid = threads_api.post(post["text"], urls)
        result = {"id": pid, "posted_at": dt.datetime.now(KST).isoformat()}
        if post.get("reply"):
            result["reply_id"] = threads_api.post(post["reply"]["text"], reply_to=pid)
        dest = ROOT / "published" / f.parent.parent.name / f.parent.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f.parent), dest)
        (dest / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[게시] {dest} → {pid}")
    for d in (ROOT / "queue").glob("*"):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    sys.exit(1 if failed else 0)  # 차단이 있으면 Actions 실패로 표시해 알 수 있게


if __name__ == "__main__":
    main()
