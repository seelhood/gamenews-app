# Простой словарь для перевода русских названий в английские
# Простой словарь для перевода русских названий в английские
GAME_DICT = {
    "ведьмак": "witcher",
    "дота": "dota",
    "кс": "counter-strike",
    "го": "counter-strike",
    "дум": "doom",
    "гта": "gta",
    "скайрим": "skyrim",
    "паук": "spider-man",
    "человек паук": "spider-man",
    "бог войны": "god of war",
    "мортал": "mortar kombat", # Исправлена опечатка
    "киберпанк": "cyberpunk"
}

def translate_query(query: str) -> str:
    q = query.lower().strip()
    return GAME_DICT.get(q, query)

def get_game_aliases(title: str) -> list[str]:
    """Возвращает все возможные названия игры (русские и английские)"""
    title_lower = title.lower().strip()
    aliases = {title_lower}
    
    # Если в названии игры есть ключи из словаря (например, "Dota 2" содержит "dota")
    for ru, en in GAME_DICT.items():
        if ru in title_lower or en in title_lower:
            aliases.add(ru)
            aliases.add(en)
            
    return list(aliases)