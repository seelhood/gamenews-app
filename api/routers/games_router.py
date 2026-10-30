from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.auth import get_current_user, get_current_admin_user
from api.schemas.game_schema import GameCreate, GameUpdate, GameOut
from database.repositories.game_repository import GameRepository
from database.models.game import Game
from database.models.user_game import UserGame

router = APIRouter(prefix="/games", tags=["games"])

@router.get("/", response_model=list[GameOut])
def list_games(limit: int = Query(50, ge=1, le=200),
               offset: int = Query(0, ge=0),
               db: Session = Depends(get_db)):
    return GameRepository(db).get_all()[offset:offset+limit]

# ВАЖНО: /my должен идти ДО /{game_id}, иначе FastAPI перепутает
@router.get("/my", response_model=list[GameOut])
def list_my_games(db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    return (db.query(Game).join(UserGame)
            .filter(UserGame.user_id == current_user.id).all())

@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = GameRepository(db).get_by_id(game_id)
    if not game:
        raise HTTPException(404, "Игра не найдена")
    return game

@router.post("/", response_model=GameOut, status_code=201)
def create_game(data: GameCreate, db: Session = Depends(get_db),
                admin=Depends(get_current_admin_user)):
    repo = GameRepository(db)
    if repo.get_by_title(data.title):
        raise HTTPException(400, "Игра уже существует")
    return repo.create(data.title, data.genre)

@router.put("/{game_id}", response_model=GameOut)
def update_game(game_id: int, data: GameUpdate,
                db: Session = Depends(get_db),
                admin=Depends(get_current_admin_user)):
    repo = GameRepository(db)
    game = repo.get_by_id(game_id)
    if not game:
        raise HTTPException(404, "Игра не найдена")
    if data.title is not None: game.title = data.title
    if data.genre is not None: game.genre = data.genre
    db.commit()
    db.refresh(game)
    return game

@router.delete("/{game_id}", status_code=204)
def delete_game(game_id: int, db: Session = Depends(get_db),
                admin=Depends(get_current_admin_user)):
    if not GameRepository(db).delete(game_id):
        raise HTTPException(404, "Игра не найдена")
    return None

@router.post("/{game_id}/track", status_code=201)
def track_game(game_id: int, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    if not db.query(Game).filter(Game.id == game_id).first():
        raise HTTPException(404, "Игра не найдена")
    existing = db.query(UserGame).filter(
        UserGame.user_id == current_user.id, UserGame.game_id == game_id
    ).first()
    if existing:
        raise HTTPException(400, "Игра уже отслеживается")
    db.add(UserGame(user_id=current_user.id, game_id=game_id))
    db.commit()
    return {"status": "tracked", "game_id": game_id}

@router.delete("/{game_id}/track", status_code=204)
def untrack_game(game_id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    link = db.query(UserGame).filter(
        UserGame.user_id == current_user.id, UserGame.game_id == game_id
    ).first()
    if not link:
        raise HTTPException(404, "Игра не отслеживается")
    db.delete(link)
    db.commit()
    return None