from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.auth import get_current_user
from api.schemas.favorite_schema import FavoriteCreate, FavoriteOut
from database.repositories.favorite_repository import FavoriteRepository
from database.models.news import News

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("/", response_model=list[FavoriteOut])
def list_favorites(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = FavoriteRepository(db)
    favs = repo.get_user_favorites(current_user.id)[offset:offset+limit]
    return [
        FavoriteOut(
            id=f.id, news_id=f.news_id,
            news_title=f.news.title if f.news else "—",
            saved_title=f.saved_title, added_date=f.added_date,
        ) for f in favs
    ]

@router.post("/", response_model=FavoriteOut, status_code=201)
def add_favorite(data: FavoriteCreate, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    news = db.query(News).filter(News.id == data.news_id).first()
    if not news:
        raise HTTPException(404, "Новость не найдена")
    repo = FavoriteRepository(db)
    if repo.is_favorite(current_user.id, data.news_id):
        raise HTTPException(400, "Уже в избранном")
    fav = repo.add(current_user.id, data.news_id)
    if data.saved_title or data.saved_text:
        fav.saved_title = data.saved_title
        fav.saved_text = data.saved_text
        db.commit()
        db.refresh(fav)
    return FavoriteOut(
        id=fav.id, news_id=fav.news_id, news_title=news.title,
        saved_title=fav.saved_title, added_date=fav.added_date,
    )

@router.delete("/{news_id}", status_code=204)
def remove_favorite(news_id: int, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    if not FavoriteRepository(db).remove(current_user.id, news_id):
        raise HTTPException(404, "Не найдено в избранном")
    return None