import requests
from config import API_URL

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
            headers = {"Authorization": f"Bearer {token}"}
            me = requests.get(f"{API_URL}/users/me", headers=headers, timeout=10).json()
            return {"success": True, "user": me, "token": token}
        return {"success": False, "error": "Неверный логин или пароль"}
    except Exception as e:
        return {"success": False, "error": f"Нет связи с сервером: {e}"}

# --- Функции для работы с новостями и играми (через API) ---
def get_my_games(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_URL}/games/my", headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else []

def add_game(token, title):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API_URL}/games", json={"title": title}, headers=headers, timeout=10)
    return r.json()

def get_news(token, search=None, source=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if search: params["search"] = search
    if source: params["source"] = source
    r = requests.get(f"{API_URL}/news/", headers=headers, params=params, timeout=10)
    return r.json().get("items", []) if r.status_code == 200 else []