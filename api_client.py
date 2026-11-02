import requests
from config import API_URL

def _headers(token):
    return {"Authorization": f"Bearer {token}"} if token else {}

def register(username, email, password):
    try:
        r = requests.post(f"{API_URL}/auth/register", json={
            "username": username, "email": email, "password": password
        }, timeout=10)
        if r.status_code == 200:
            return {"success": True}
        return {"success": False, "error": r.json().get("detail", "Ошибка регистрации")}
    except Exception as e:
        return {"success": False, "error": f"Нет связи с сервером: {e}"}

def login(username, password):
    try:
        r = requests.post(f"{API_URL}/auth/login", data={
            "username": username, "password": password
        }, timeout=10)
        if r.status_code == 200:
            data = r.json()
            token = data["access_token"]
            me = requests.get(f"{API_URL}/users/me", headers=_headers(token), timeout=10).json()
            return {"success": True, "user": me, "token": token}
        return {"success": False, "error": "Неверный логин или пароль"}
    except Exception as e:
        return {"success": False, "error": f"Нет связи с сервером: {e}"}

# --- ИГРЫ ---
def get_my_games(token):
    try:
        r = requests.get(f"{API_URL}/games/my", headers=_headers(token), timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def add_game(token, title):
    try:
        r = requests.post(f"{API_URL}/games/add", json={"title": title}, headers=_headers(token), timeout=10)
        return r.json() if r.status_code in (200, 201) else {"error": "Ошибка добавления"}
    except Exception as e:
        return {"error": str(e)}

def delete_game(token, game_id):
    try:
        r = requests.delete(f"{API_URL}/games/{game_id}/track", headers=_headers(token), timeout=10)
        return r.status_code == 204
    except:
        return False

# --- НОВОСТИ ---
def get_news(token, search=None, source=None, limit=100):
    try:
        params = {"per_page": limit}
        if search: params["search"] = search
        if source and source != "Все": params["source"] = source
        r = requests.get(f"{API_URL}/news/", headers=_headers(token), params=params, timeout=10)
        return r.json().get("items", []) if r.status_code == 200 else []
    except:
        return []

def get_news_detail(token, news_id):
    try:
        r = requests.get(f"{API_URL}/news/{news_id}", headers=_headers(token), timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# --- ИЗБРАННОЕ ---
def get_favorites(token):
    try:
        r = requests.get(f"{API_URL}/favorites/", headers=_headers(token), timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def toggle_favorite(token, news_id, saved_title=None, saved_text=None):
    try:
        r = requests.get(f"{API_URL}/favorites/", headers=_headers(token), timeout=10)
        if r.status_code == 200:
            for f in r.json():
                if f["news_id"] == news_id:
                    requests.delete(f"{API_URL}/favorites/{news_id}", headers=_headers(token), timeout=10)
                    return "removed"
        payload = {"news_id": news_id}
        if saved_title: payload["saved_title"] = saved_title
        if saved_text: payload["saved_text"] = saved_text
        r = requests.post(f"{API_URL}/favorites/", json=payload, headers=_headers(token), timeout=10)
        return "added" if r.status_code == 201 else "error"
    except:
        return "error"
