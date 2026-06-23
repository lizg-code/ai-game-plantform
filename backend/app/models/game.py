from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    cover_url = Column(String(500), default="")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tags = Column(JSON, default=list)  # ["puzzle", "adventure"]
    status = Column(
        SQLEnum("draft", "generating", "published", "failed", name="game_status_enum"),
        default="draft",
        nullable=False,
    )
    remote_url = Column(String(500), default="")  # MinIO URL for the game HTML
    game_type = Column(String(50), default="")
    design_doc = Column(JSON, default=dict)  # Agent-generated design document
    user_prompt = Column(Text, default="")  # Original user creative input
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Game(id={self.id}, title='{self.title}', status='{self.status}')>"
