from googleapiclient.discovery import build
from config import API_KEY

def enrich_youtube_records(records: list[dict]) -> list[dict]:
    ids = [r["video_id"] for r in records if r.get("video_id")]
    if not ids:
        return records

    yt = build("youtube", "v3", developerKey=API_KEY)

    resp = yt.videos().list(
        part="statistics,snippet",
        id=",".join(ids[:50])
    ).execute()

    api_map = {item["id"]: item for item in resp.get("items", [])}

    for r in records:
        api = api_map.get(r.get("video_id"))
        if not api:
            continue

        stats = api.get("statistics", {})
        snippet = api.get("snippet", {})

        r["views_api"] = int(stats.get("viewCount", 0))
        r["likes_api"] = int(stats.get("likeCount", 0))
        r["comments_api"] = int(stats.get("commentCount", 0))
        r["published_at"] = snippet.get("publishedAt")

    return records
