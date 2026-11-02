from sqlalchemy.orm import Session
from database.models.news import News


class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, link: str, description: str = None, game_id: int = None, source_id: int = None, image_url: str = None) -> News:
        news = News(title=title, link=link, description=description, game_id=game_id, source_id=source_id, image_url=image_url)
        self.session.add(news)
        self.session.commit()
        self.session.refresh(news)
        return news

    def get_by_id(self, news_id: int):
        return self.session.query(News).filter(News.id == news_id).first()

    def get_all(self, limit: int = 50):
        return self.session.query(News).order_by(News.id.desc()).limit(limit).all()

    def get_by_games_and_source(self, game_ids: list, source_name: str = None, limit: int = 100):
        if not game_ids:
            return []

        print(f"   [REPO] Ищу новости для game_ids: {game_ids}, source: {source_name}")

        query = self.session.query(News).filter(News.game_id.in_(game_ids))

        if source_name and source_name != "Все":
            from database.models.source import Source
            query = query.join(Source).filter(Source.name == source_name)

        result = query.order_by(News.id.desc()).limit(limit).all()
        print(f"   [REPO] Найдено в базе: {len(result)}")
        return result

    def exists_by_link(self, link: str) -> bool:
        return self.session.query(News).filter(News.link == link).first() is not None

    def delete(self, news_id: int) -> bool:
        news = self.get_by_id(news_id)
        if not news:
            return False
        self.session.delete(news)
        self.session.commit()
        return True