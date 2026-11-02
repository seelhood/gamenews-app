from sqlalchemy.orm import Session
from database.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, user_id: int, news_id: int) -> Favorite:
        fav = Favorite(user_id=user_id, news_id=news_id)
        self.session.add(fav)
        self.session.commit()
        self.session.refresh(fav)
        return fav

    def remove(self, user_id: int, news_id: int) -> bool:
        fav = (
            self.session.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.news_id == news_id)
            .first()
        )
        if not fav:
            return False
        self.session.delete(fav)
        self.session.commit()
        return True

    def get_user_favorites(self, user_id: int):
        return (
            self.session.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.added_date.desc()).all()
        )

    def is_favorite(self, user_id: int, news_id: int) -> bool:
        return (
            self.session.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.news_id == news_id)
            .first() is not None
        )