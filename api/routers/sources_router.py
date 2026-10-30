from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.auth import get_current_admin_user
from api.schemas.source_schema import SourceCreate, SourceUpdate, SourceOut
from database.repositories.source_repository import SourceRepository

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("/", response_model=list[SourceOut])
def list_sources(limit: int = Query(50, ge=1, le=200),
                 offset: int = Query(0, ge=0),
                 db: Session = Depends(get_db)):
    return SourceRepository(db).get_all()[offset:offset+limit]

@router.get("/{source_id}", response_model=SourceOut)
def get_source(source_id: int, db: Session = Depends(get_db)):
    src = SourceRepository(db).get_by_id(source_id)
    if not src:
        raise HTTPException(404, "Источник не найден")
    return src

@router.post("/", response_model=SourceOut, status_code=201)
def create_source(data: SourceCreate, db: Session = Depends(get_db),
                  admin=Depends(get_current_admin_user)):
    repo = SourceRepository(db)
    if repo.get_by_name(data.name):
        raise HTTPException(400, "Источник с таким именем уже есть")
    return repo.create(data.name, data.rss_url)

@router.put("/{source_id}", response_model=SourceOut)
def update_source(source_id: int, data: SourceUpdate,
                  db: Session = Depends(get_db),
                  admin=Depends(get_current_admin_user)):
    repo = SourceRepository(db)
    src = repo.get_by_id(source_id)
    if not src:
        raise HTTPException(404, "Источник не найден")
    if data.name is not None: src.name = data.name
    if data.rss_url is not None: src.rss_url = data.rss_url
    if data.is_active is not None: src.is_active = data.is_active
    db.commit()
    db.refresh(src)
    return src

@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db),
                  admin=Depends(get_current_admin_user)):
    if not SourceRepository(db).delete(source_id):
        raise HTTPException(404, "Источник не найден")
    return None