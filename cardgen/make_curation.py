"""다수결 정리글 만들기: 순위 JSON → 카드 이미지 2장 + 게시 대기열(post.json).

사용: python3 cardgen/make_curation.py rankings/2026-12-16.json
순위 JSON 예시(rankings/example.json 참고):
{"date": "2026-12-16", "slot": "1930",
 "question": "자취 3년 넘은 사람들, '진작 살걸' 싶었던 물건",
 "comments": 214, "hook": "지난주 '진작 살걸' 질문에 댓글 214개.",
 "items": [{"name": "욕실 스퀴지", "votes": 31, "why": "물기 안 남아 곰팡이 청소가 줄었다는 말이 제일 많았어",
            "link": "https://link.coupang.com/a/xxxx"}, ...]}
- votes: 같은 사람 중복 없이 센 표(data/replies의 voter 해시 기준)
- why: 댓글들을 요약한 문장(아이디·원문 그대로 인용 금지)
- link: 쿠팡 파트너스 링크(없으면 그 항목은 답글에서 '링크 없음')
"""
import html, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@500;700;900&display=block');
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#f4f1e8;font-family:'Noto Sans KR',sans-serif;color:#1e2a24;
 padding:84px 80px;display:flex;flex-direction:column;gap:36px}
.tag{font-family:'Do Hyeon';font-size:40px;color:#c2412d;border:4px solid #c2412d;display:inline-block;
 padding:6px 22px;border-radius:10px;transform:rotate(-2deg);align-self:flex-start}
h1{font-family:'Do Hyeon';font-weight:400;font-size:84px;line-height:1.15}
.sub{font-size:34px;color:#5d6a62;font-weight:500}
.row{display:grid;grid-template-columns:96px 1fr auto;align-items:center;gap:24px;background:#fff;
 border-radius:22px;padding:24px 32px}
.rk{font-family:'Do Hyeon';font-size:64px;color:#1f7a55;text-align:center}
.nm{font-size:44px;font-weight:900;line-height:1.2}
.bar{height:16px;border-radius:8px;background:#1f7a55;margin-top:12px}
.vt{font-size:38px;font-weight:700;color:#1f7a55;white-space:nowrap}
.first{background:#1f7a55;color:#fff}.first .rk,.first .vt{color:#fff}.first .bar{background:#fff}
.q{background:#fff;border-radius:22px;padding:36px 40px;font-size:42px;font-weight:700;line-height:1.5}
.q small{display:block;font-size:30px;color:#5d6a62;font-weight:500;margin-top:10px}
.foot{margin-top:auto;font-size:26px;color:#5d6a62;display:flex;justify-content:space-between}
"""


def page(body):
    return f"<!doctype html><meta charset='utf-8'><style>{CSS}</style><body>{body}</body>"


def card_rank(r):
    top = r["items"][:5]
    mx = max(i["votes"] for i in top)
    rows = "".join(
        f"<div class='row{' first' if n == 0 else ''}'><div class='rk'>{n+1}</div>"
        f"<div><div class='nm'>{html.escape(i['name'])}</div><div class='bar' style='width:{int(100*i['votes']/mx)}%'></div></div>"
        f"<div class='vt'>{i['votes']}표</div></div>" for n, i in enumerate(top))
    return page(f"<div class='tag'>살림 다수결</div><h1>{html.escape(r['question'])}</h1>"
                f"<div class='sub'>댓글 {r['comments']}개를 세어 봤어요</div>{rows}"
                f"<div class='foot'><span>@salim.dasugyeol</span><span>같은 사람 중복 표는 1표로</span></div>")


def card_why(r):
    qs = "".join(f"<div class='q'>“{html.escape(i['why'])}”<small>{i['votes']}표 · {html.escape(i['name'])}</small></div>"
                 for i in r["items"][:3])
    return page(f"<div class='tag'>왜 골랐을까</div><h1>댓글에서 제일 많이<br>나온 이유</h1>{qs}"
                f"<div class='foot'><span>@salim.dasugyeol</span><span>댓글 내용을 요약했어요</span></div>")


def shoot(html_path, png_path):
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const p=await b.newPage({viewport:{width:1080,height:1350}});"
          f"await p.goto('file://{html_path}');await p.waitForTimeout(1500);"
          f"await p.screenshot({{path:'{png_path}',type:'jpeg',quality:90}});await b.close();}})();")
    subprocess.run(["node", "-e", js], check=True)


def main(src):
    r = json.loads(Path(src).read_text(encoding="utf-8"))
    out = ROOT / "queue" / r["date"] / r.get("slot", "1930")
    out.mkdir(parents=True, exist_ok=True)
    imgs = []
    for n, fn in enumerate((card_rank, card_why), 1):
        h = out / f"card{n}.html"
        h.write_text(fn(r), encoding="utf-8")
        shoot(h, out / f"card{n}.jpg")
        h.unlink()
        imgs.append(f"queue/{r['date']}/{r.get('slot','1930')}/card{n}.jpg")
    top = r["items"]
    text = (f"{check.AD_PREFIX}\n{r['hook']}\n\n"
            + "\n".join(f"{n+1}위 {i['name']} ({i['votes']}표)" for n, i in enumerate(top[:3]))
            + "\n\n순위 전체랑 링크는 답글에 👇")
    reply = ("\n".join(f"{n+1}. {i['name']} {i['link'] if i.get('link') else '(링크 없음)'}" for n, i in enumerate(top[:5]))
             + f"\n\n{check.FTC}")
    post = {"type": "curation", "text": text, "images": imgs, "reply": {"text": reply}, "source": str(src)}
    bad = check.problems(post)
    (out / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=1), encoding="utf-8")
    print("생성:", out, "| 검사:", "통과" if not bad else bad)


if __name__ == "__main__":
    main(sys.argv[1])
