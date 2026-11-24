"""Threads 공식 API 호출 모음 (graph.threads.net)."""
import json, os, time, urllib.parse, urllib.request

BASE = "https://graph.threads.net/v1.0"


def _token():
    t = os.environ.get("THREADS_TOKEN", "").strip()
    if not t:
        raise SystemExit("THREADS_TOKEN 시크릿이 없습니다.")
    return t


def _call(method, path, params=None):
    params = dict(params or {})
    params["access_token"] = _token()
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{BASE}{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{BASE}{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Threads API {e.code} {path}: {body}") from None


def _container(params):
    return _call("POST", "/me/threads", params)["id"]


def _publish(creation_id, wait):
    time.sleep(wait)  # 메타 권장: 이미지 컨테이너는 처리 시간을 둔 뒤 게시
    return _call("POST", "/me/threads_publish", {"creation_id": creation_id})["id"]


def post(text, image_urls=(), reply_to=None):
    """글 1개 게시. 이미지 0장=텍스트, 1장=이미지, 2장+=캐러셀. 게시된 글 id 반환."""
    base = {"text": text}
    if reply_to:
        base["reply_to_id"] = reply_to
    image_urls = list(image_urls)
    if not image_urls:
        cid = _container({**base, "media_type": "TEXT"})
        return _publish(cid, 2)
    if len(image_urls) == 1:
        cid = _container({**base, "media_type": "IMAGE", "image_url": image_urls[0]})
        return _publish(cid, 20)
    children = [
        _container({"media_type": "IMAGE", "image_url": u, "is_carousel_item": "true"})
        for u in image_urls
    ]
    time.sleep(10)
    cid = _container({**base, "media_type": "CAROUSEL", "children": ",".join(children)})
    return _publish(cid, 20)


def my_posts(since_unix):
    out, params = [], {"fields": "id,text,timestamp,permalink", "since": since_unix, "limit": 50}
    res = _call("GET", "/me/threads", params)
    out += res.get("data", [])
    return out


def replies(media_id):
    res = _call("GET", f"/{media_id}/conversation",
                {"fields": "id,text,timestamp,username,root_post", "reverse": "false"})
    return res.get("data", [])


def publishing_limit():
    return _call("GET", "/me/threads_publishing_limit", {"fields": "quota_usage,config"})
