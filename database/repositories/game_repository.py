from sqlalchemy.orm import Session
from database.models.game import Game
from sqlalchemy import func

class GameRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, genre: str = None) -> Game:
        game = Game(title=title, genre=genre)
        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)
        return game

    def get_by_id(self, game_id: int):
        return self.session.query(Game).filter(Game.id == game_id).first()

    def get_by_title(self, title: str):
        # Ищем без учета регистра (ilike)
        return self.session.query(Game).filter(func.lower(Game.title) == title.lower()).first()

    def get_all(self):
        return self.session.query(Game).all()

    def update(self, game_id: int, new_title: str) -> bool:
        game = self.get_by_id(game_id)
        if not game:
            return False
        game.title = new_title
        self.session.commit()
        return True

    def delete(self, game_id: int) -> bool:
        game = self.get_by_id(game_id)
        if not game:
            return False
        self.session.delete(game)
        self.session.commit()
        return True