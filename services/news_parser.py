"""
Парсер RSS-лент.
Тянет новости из интернета и сохраняет в PostgreSQL.
"""

import re
import html
import feedparser
import requests
from database.session import SessionLocal
from database.repositories.news_repository import NewsRepository
from database.repositories.source_repository import SourceRepository
from utils.translator import GAME_DICT
from utils.translator import get_game_aliases



RSS_SOURCES = [
    {"name": "DTF",          "url": "https://dtf.ru/rss"}, # <--- ИСПРАВЛЕНА ССЫЛКА
    {"name": "StopGame",     "url": "https://rss.stopgame.ru/rss_news.xml"},
    {"name": "IGN",          "url": "https://feeds.ign.com/ign/games-all"},
    {"name": "PC Gamer",     "url": "https://www.pcgamer.com/rss/"},
    {"name": "Eurogamer",    "url": "https://www.eurogamer.net/feed"},
    {"name": "Polygon",      "url": "https://www.polygon.com/rss/index.xml"},
    {"name": "GameSpot",     "url": "https://www.gamespot.com/feeds/news/"},
    {"name": "Kotaku",       "url": "https://kotaku.com/rss"},
]

# Заголовки, чтобы сайты думали, что мы обычный браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_from_rss(url: str) -> list:
    try:
        # Используем requests с заголовками, чтобы сайты не блокировали
        response = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return []

    items = []

    for entry in feed.entries[:100]:
        # --- ПОИСК КАРТИНКИ В RSS ---
        img_url = None
        if 'media_content' in entry:
            img_url = entry.media_content[0].get('url')
        elif 'enclosures' in entry:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image'):
                    img_url = enc.get('href')
                    break
        elif 'links' in entry:
            for link in entry.links:
                if link.get('type', '').startswith('image'):
                    img_url = link.get('href')
                    break
        # ----------------------------

        # --- ОЧИСТКА ТЕКСТА ОТ HTML ---
        raw_desc = entry.get("summary", "")
        # Удаляем все теги (все, что в <...>)
        clean_desc = re.sub(r'<[^>]+>', '', raw_desc)
        # Превращаем HTML-мнемоники (&amp;, &quot;, &nbsp;) в обычные символы
        clean_desc = html.unescape(clean_desc)
        # Обрезаем до 500 символов и убираем лишние пробелы по краям
        clean_desc = clean_desc.strip()[:500]
        # ------------------------------

        items.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", "").strip(),
            "description": clean_desc,  # <--- Используем очищенный текст
            "published": entry.get("published", ""),
            "image_url": img_url
        })

    return items



def get_game_aliases(title: str) -> list[str]:
    """Возвращает все возможные названия игры (русские и английские)"""
    title_lower = title.lower().strip()
    aliases = {title_lower}
    
    # Ищем прямое совпадение (если игра добавлена на русском)
    if title_lower in GAME_DICT:
        aliases.add(GAME_DICT[title_lower])
        
    # Ищем обратное совпадение (если игра добавлена на английском)
    for ru, en in GAME_DICT.items():
        if title_lower == en:
            aliases.add(ru)
            
    return list(aliases)

def save_news_to_db(source_name: str, source_url: str, news_items: list) -> int:
    db = SessionLocal()
    added = 0
    try:
        source_repo = SourceRepository(db)
        source = source_repo.get_by_name(source_name)
        if not source:
            source = source_repo.create(source_name, source_url)

        from database.models.game import Game
        all_games = db.query(Game).all()
        
        if not all_games:
            print("  [ВНИМАНИЕ] В базе нет ни одной игры! Новости сохранятся без привязки.")

        news_repo = NewsRepository(db)
        for item in news_items:
            if not item["link"] or news_repo.exists_by_link(item["link"]):
                continue

            matched_game_id = None
            full_text = (item["title"] + " " + (item["description"] or "")).lower()
            
            # Ищем совпадения
            for game in all_games:
                aliases = get_game_aliases(game.title)
                if any(alias in full_text for alias in aliases):
                    matched_game_id = game.id
                    print(f"  [MATCH] '{item['title'][:30]}...' -> {game.title}")
                    break

            news_repo.create(
                title=item["title"],
                link=item["link"],
                description=item["description"],
                source_id=source.id,
                image_url=item.get("image_url"),
                game_id=matched_game_id
            )
            added += 1
    finally:
        db.close()
    return added

# В файле services/news_parser.py


def sync_all_sources() -> dict:
    """Синхронизирует все источники из RSS_SOURCES."""
    total_added = 0
    report = []

    for src in RSS_SOURCES:
        print(f"[RSS] Загружаю {src['name']}...")
        try:
            items = fetch_from_rss(src["url"])
            added = save_news_to_db(src["name"], src["url"], items)
            total_added += added
            report.append({"source": src["name"], "fetched": len(items), "added": added})
            print(f"  → {len(items)} получено, {added} добавлено")
        except Exception as e:
            print(f"  [Ошибка] {e}")
            report.append({"source": src["name"], "error": str(e)})

    return {"total_added": total_added, "details": report}


if __name__ == "__main__":
    print("=" * 50)
    print("  Синхронизация новостей GameNews")
    print("=" * 50)
    result = sync_all_sources()
    print(f"\n[OK] Всего добавлено: {result['total_added']}")