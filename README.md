# 살림 다수결 (스레드 자동 게시)

"다들 뭐 써?"라고 묻고, 실제 댓글을 세어 정리하는 살림 계정 @salim.dasugyeol.

- `queue/<날짜>/<HHMM>/post.json` → 시간이 되면 `.github/workflows/post.yml`(12:30·19:30·22:30 KST)이 게시 → `published/`로 이동
- 게시 전 `scripts/check.py`가 막는 것: 후기 위장 표현, 금지 카테고리, 링크 글의 광고 표시·공정위 문구 누락, 500자 초과, 하루 3개 초과. 막힌 글은 `held/`에 이유와 함께 보관
- `collect.yml`(23:50 KST)이 최근 14일 질문글 댓글을 `data/replies/`에 저장(아이디는 해시로만)
- 시크릿: `THREADS_TOKEN`
- 원칙: 써 보지 않은 물건을 써 본 척하지 않는다. 평가는 "댓글 ○표", "쿠팡 평점(날짜 기준)"처럼 출처를 붙인다.
