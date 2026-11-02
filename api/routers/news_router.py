from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.auth import get_current_user, get_current_admin_user
from api.schemas.news_schema import NewsCreate, NewsUpdate, NewsOut, NewsListOut
from database.repositories.news_repository import NewsRepository
from services.news_service import NewsService
from services.news_lifecycle import NotFoundError, InvalidTransitionError
from database.models.user import User
from api.schemas.news_schema import NewsStatusUpdate



router = APIRouter(prefix="/news", tags=["news"])

@router.get("/", response_model=NewsListOut)
def list_news(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), search: str | None = Query(None), source: str | None = Query(None), db: Session = Depends(get_db)):
    from database.models.news import News
    from database.models.source import Source
    query = db.query(News)
    if search: query = query.filter(News.title.ilike(f"%{search}%"))
    if source: query = query.join(Source).filter(Source.name == source)
    
    total = query.count()
    items = query.order_by(News.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    items_out = [NewsOut(id=n.id, title=n.title, link=n.link, description=n.description, published=n.published, status=n.status, created_at=n.created_at, source=n.source.name if n.source else None) for n in items]
    return NewsListOut(total=total, page=page, per_page=per_page, items=items_out)

@router.get("/{news_id}", response_model=NewsOut)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = NewsRepository(db).get_by_id(news_id)
    if not news: raise HTTPException(404, "Новость не найдена")
    return NewsOut(id=news.id, title=news.title, link=news.link, description=news.description, published=news.published, status=news.status, created_at=news.created_at, source=news.source.name if news.source else None)

@router.post("/", response_model=NewsOut, status_code=201)
def create_news(data: NewsCreate, db: Session = Depends(get_db)):
    repo = NewsRepository(db)
    if repo.exists_by_link(data.link): raise HTTPException(400, "Новость с такой ссылкой уже есть")
    return repo.create(title=data.title, link=data.link, description=data.description, game_id=data.game_id, source_id=data.source_id)

@router.put("/{news_id}", response_model=NewsOut)
def update_news(news_id: int, data: NewsUpdate, db: Session = Depends(get_db)):
    repo = NewsRepository(db)
    news = repo.get_by_id(news_id)
    if not news: raise HTTPException(404, "Новость не найдена")
    
    if data.title is not None: news.title = data.title
    if data.description is not None: news.description = data.description
    if data.status is not None and data.status != news.status:
        try: NewsService().change_status(news_id, data.status)
        except NotFoundError as e: raise HTTPException(404, str(e))
        except InvalidTransitionError as e: raise HTTPException(409, str(e))
        
    db.commit()
    db.refresh(news)
    return news

@router.delete("/{news_id}", status_code=204)
def delete_news(news_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)): # <--- ТОЛЬКО АДМИН
    if not NewsRepository(db).delete(news_id): raise HTTPException(404, "Новость не найдена")
    return None

@router.post("/{news_id}/status")
def change_status(news_id: int, data: NewsStatusUpdate,
                  admin=Depends(get_current_admin_user)):
    try:
        return NewsService().change_status(news_id, data.status)
    except NotFoundError as e: raise HTTPException(404, str(e))
    except InvalidTransitionError as e: raise HTTPException(409, str(e))