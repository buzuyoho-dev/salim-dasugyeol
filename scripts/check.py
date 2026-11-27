"""게시 차단 검사. 하나라도 걸리면 게시하지 않는다."""
import re

AD_PREFIX = "[광고 · 쿠팡 파트너스]"
FTC = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

# 써 보지 않은 물건을 써 본 척하는 표현 (표시광고법)
FAKE_REVIEW = [r"써\s?봤", r"써\s?보니", r"사용해\s?보", r"사용\s?해봤", r"내돈내산", r"직접\s?(써|사용|구매)",
               r"제가\s?(써|샀|산)", r"실사용\s?후기", r"한\s?달\s?(째|동안)\s?(쓰|사용)", r"재구매\s?했"]
# 효능 표현이 법으로 까다롭거나 잘못 추천하면 해가 큰 카테고리
BANNED_CATEGORY = ["영양제", "유산균", "비타민", "다이어트", "건강기능", "화장품", "세럼", "앰플", "크림",
                   "의약", "탈모", "카시트", "젖병", "분유", "보행기"]
# 댓글·반응을 부탁하거나 유도하는 문구(대표 규칙 2026-11-27: 질문까지만, 요청 문구 금지)
ASK_REACTION = [r"댓글\s?(로|을|좀|부탁|달|남|써|적)", r"알려\s?줘", r"알려\s?주", r"남겨\s?줘", r"남겨\s?주", r"적어\s?줘", r"적어\s?주",
                r"달아\s?줘", r"달아\s?주", r"추천해\s?줘", r"추천해\s?주", r"하나씩만", r"손\s?🙋", r"모여",
                r"팔로우", r"좋아요", r"저장해", r"공유해", r"눌러", r"참여해", r"투표해"]
MAX_LEN = 500  # Threads 텍스트 한도


def problems(post):
    """post: dict(type, text, images, reply). 문제 목록 반환(빈 목록이면 통과)."""
    p = []
    text = post.get("text", "")
    reply = (post.get("reply") or {}).get("text", "")
    all_text = text + "\n" + reply
    if not text.strip():
        p.append("본문 없음")
    for t, name in ((text, "본문"), (reply, "답글")):
        if len(t) > MAX_LEN:
            p.append(f"{name} {len(t)}자 (500자 초과)")
    for pat in FAKE_REVIEW:
        if re.search(pat, all_text):
            p.append(f"후기 위장 표현: {pat}")
    for w in BANNED_CATEGORY:
        if w in all_text:
            p.append(f"금지 카테고리 단어: {w}")
    for pat in ASK_REACTION:
        if re.search(pat, text):
            p.append(f"반응 유도 문구: {pat}")
    has_link = "http" in all_text or post.get("type") == "curation"
    if has_link:
        if not text.startswith(AD_PREFIX):
            p.append("링크 글인데 첫 줄 광고 표시 없음")
        if FTC not in reply:
            p.append("링크 답글에 공정위 문구 없음")
        if "http" in text:
            p.append("링크는 본문이 아니라 답글에만")
    if post.get("type") in ("question", "vs") and "http" in all_text:
        p.append("질문글에 링크 금지")
    return p
