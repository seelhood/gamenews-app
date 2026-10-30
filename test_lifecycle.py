"""
Проверка жизненного цикла новости.
"""
from services.news_service import NewsService
from services.news_lifecycle import NotFoundError, InvalidTransitionError


def run():
    svc = NewsService()

    print("=" * 55)
    print(" Тест жизненного цикла новости")
    print("=" * 55)

    news_list = svc.list_news(limit=1)
    if not news_list:
        print("Нет новостей в БД. Запусти парсер сначала.")
        return

    nid = news_list[0]["id"]
    print(f"\n[1] Новость id={nid}")

    # CREATED → ACTIVE
    try:
        r = svc.change_status(nid, "ACTIVE")
        print(f"    CREATED → ACTIVE: OK ({r['status']})")
    except Exception as e:
        print(f"    CREATED → ACTIVE: {e}")

    # ACTIVE → COMPLETED
    try:
        r = svc.change_status(nid, "COMPLETED")
        print(f"    ACTIVE → COMPLETED: OK ({r['status']})")
    except Exception as e:
        print(f"    ACTIVE → COMPLETED: {e}")

    # COMPLETED → ACTIVE (запрещено)
    try:
        svc.change_status(nid, "ACTIVE")
        print("    COMPLETED → ACTIVE: ОШИБКА! Должно было упасть")
    except InvalidTransitionError as e:
        print(f"    COMPLETED → ACTIVE: [409] {e}")

    # Несуществующая новость (404)
    try:
        svc.change_status(99999, "ACTIVE")
    except NotFoundError as e:
        print(f"    id=99999: [404] {e}")


if __name__ == "__main__":
    run()