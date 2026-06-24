from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class GameCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []


class GameResponse(BaseModel):
    id: int
    title: str
    description: str
    cover_url: str
    author_id: int
    author_nickname: str = ""
    tags: List[str]
    status: str
    remote_url: Optional[str] = ""
    game_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    total: int
    games: List[GameResponse]


class GenerateRequest(BaseModel):
    user_prompt: str
    materials: Optional[List[str]] = []  # List of material URLs


class GenerateResponse(BaseModel):
    game_id: int
    status: str
    message: str


class AgentLogResponse(BaseModel):
    id: int
    game_id: int
    step_name: str
    step_order: int
    status: str
    input_data: dict
    output_data: dict
    error_message: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


class GameStatusResponse(BaseModel):
    game_id: int
    status: str
    remote_url: Optional[str] = ""
    logs: List[AgentLogResponse]
