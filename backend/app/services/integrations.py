import requests
from ..config import Config


def moodle_courses():
    if not (Config.MOODLE_URL and Config.MOODLE_TOKEN):
        raise RuntimeError("Moodle is not configured (set MOODLE_URL and MOODLE_TOKEN)")
    r = requests.get(f"{Config.MOODLE_URL}/webservice/rest/server.php", timeout=20, params={
        "wstoken": Config.MOODLE_TOKEN, "wsfunction": "core_course_get_courses", "moodlewsrestformat": "json"})
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("exception"):
        raise RuntimeError(data.get("message", "Moodle error"))
    return [{"id": c["id"], "title": c.get("fullname"), "summary": (c.get("summary") or "")[:300],
             "url": f"{Config.MOODLE_URL}/course/view.php?id={c['id']}"} for c in data if c.get("id") != 1]


def coursera_search(query):
    """Coursera search with automatic fallback when API blocks requests."""
    try:
        r = requests.get(
            "https://api.coursera.org/api/courses.v1", 
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"},
            params={"q": "search", "query": query, "limit": 10, "fields": "name,slug,description"}
        )
        if r.status_code == 200:
            elements = r.json().get("elements", [])
            if elements:
                return [{"id": e.get("id"), "title": e.get("name"), "summary": (e.get("description") or "")[:300],
                         "url": f"https://www.coursera.org/learn/{e.get('slug')}"} for e in elements]
    except Exception as e:
        print(f"Coursera API notice: {e}")

    # Fallback to direct search link when API returns 405 error
    return [{
        "id": "1",
        "title": f"Explore '{query}' courses on Coursera",
        "summary": f"Directly view relevant courses and study material for '{query}' on Coursera portal.",
        "url": f"https://www.coursera.org/search?query={query.replace(' ', '%20')}"
    }]