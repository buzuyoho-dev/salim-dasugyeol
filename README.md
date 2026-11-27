# 살림 다수결 (스레드 자동 게시)

"다들 뭐 써?"라고 묻고, 실제 댓글을 세어 정리하는 살림 계정 @salim.dasugyeol.

- `queue/<날짜>/<HHMM>/post.json` → 시간이 되면 `.github/workflows/post.yml`(12:30·19:30·22:30 KST)이 게시 → `published/`로 이동
- 게시 전 `scripts/check.py`가 막는 것: 후기 위장 표현, 금지 카테고리, 링크 글의 광고 표시·공정위 문구 누락, 500자 초과, 하루 3개 초과. 막힌 글은 `held/`에 이유와 함께 보관
- `collect.yml`(23:50 KST)이 최근 14일 질문글 댓글을 `data/replies/`에 저장(아이디는 해시로만)
- 시크릿: `THREADS_TOKEN`
- 원칙: 써 보지 않은 물건을 써 본 척하지 않는다. 평가는 "댓글 ○표", "쿠팡 평점(날짜 기준)"처럼 출처를 붙인다.
- 반응 유도 금지(대표 규칙 2026-11-27): 질문("너는 어때?")까지만. "댓글로 알려줘·남겨줘·하나씩만·손 🙋·팔로우·좋아요" 같은 요청 문구는 쓰지 않는다. check.py가 본문에서 막는다.

## 다수결 정리글 만들기 (매주 일요일)
1. `python3 cardgen/show_replies.py <날짜_슬롯>`으로 질문글 댓글을 읽고, 같은 사람 표는 1표로 세어 `rankings/<게시일>.json` 작성(형식은 `rankings/example.json`)
2. 상위 항목의 쿠팡 파트너스 링크를 `link`에 넣기(쿠팡 API 열리기 전엔 대표님이 만든 링크)
3. `python3 cardgen/make_curation.py rankings/<게시일>.json` → 카드 2장 + `queue/<게시일>/1930/post.json` 생성, 검사 통과 확인 후 push
- 표 수·이유는 실제 댓글에서만. 써 본 척 표현 금지, 댓글 원문·아이디 인용 금지(요약만)
