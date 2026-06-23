import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.game import Game
from app.models.agent_log import AgentLog
from app.models.user import User
from app.schemas.game import (
    GameResponse,
    GameListResponse,
    GenerateRequest,
    GenerateResponse,
    GameStatusResponse,
    AgentLogResponse,
)
from app.services.agent_service import create_agent_logs, run_generation
from app.utils.deps import get_current_user, get_optional_user

router = APIRouter(prefix="/api/games", tags=["Games"])


@router.get("", response_model=GameListResponse)
def list_games(
    tag: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    """List all published games, optionally filtered by tag."""
    query = db.query(Game).filter(Game.status == "published")
    if tag:
        query = query.filter(Game.tags.contains(tag))
    total = query.count()
    games = query.order_by(Game.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return GameListResponse(total=total, games=[GameResponse.model_validate(g) for g in games])


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get a single game by ID."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameResponse.model_validate(game)


@router.post("/generate", response_model=GenerateResponse)
async def generate_game(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start an Agent game generation task."""
    # Create game record
    game = Game(
        title="Generating...",
        description="",
        author_id=current_user.id,
        status="generating",
        user_prompt=req.user_prompt,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    # Initialize agent logs
    create_agent_logs(db, game.id)

    # Run generation in background
    # We need a new DB session for the background task
    from app.database import SessionLocal

    def run_in_background():
        bg_db = SessionLocal()
        try:
            asyncio.run(run_generation(bg_db, game.id))
        finally:
            bg_db.close()

    background_tasks.add_task(run_in_background)

    return GenerateResponse(
        game_id=game.id,
        status="generating",
        message="Game generation started. Poll /api/games/{id}/status for progress.",
    )


@router.get("/{game_id}/status", response_model=GameStatusResponse)
def get_game_status(game_id: int, db: Session = Depends(get_db)):
    """Get game generation status and Agent logs."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    logs = (
        db.query(AgentLog)
        .filter(AgentLog.game_id == game_id)
        .order_by(AgentLog.step_order)
        .all()
    )

    return GameStatusResponse(
        game_id=game.id,
        status=game.status,
        remote_url=game.remote_url or "",
        logs=[AgentLogResponse.model_validate(log) for log in logs],
    )


@router.post("/{game_id}/publish", response_model=GameResponse)
def publish_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish a game (change status to published)."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the game author")
    if game.status not in ("draft",):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish game with status '{game.status}'",
        )

    game.status = "published"
    db.commit()
    db.refresh(game)
    return GameResponse.model_validate(game)
