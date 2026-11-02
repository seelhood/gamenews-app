from sqlalchemy.orm import Session
from database.models.source import Source


class SourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, rss_url: str) -> Source:
        src = Source(name=name, rss_url=rss_url)
        self.session.add(src)
        self.session.commit()
        self.session.refresh(src)
        return src

    def get_by_id(self, source_id: int):
        return self.session.query(Source).filter(Source.id == source_id).first()

    def get_by_name(self, name: str):
        return self.session.query(Source).filter(Source.name == name).first()

    def get_all(self):
        return self.session.query(Source).all()

    def delete(self, source_id: int) -> bool:
        src = self.get_by_id(source_id)
        if not src:
            return False
        self.session.delete(src)
        self.session.commit()
        return True