from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from app.database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    step_name = Column(
        String(100), nullable=False
    )  # creative_analysis / game_design / code_generation / upload
    step_order = Column(Integer, nullable=False)
    status = Column(
        SQLEnum("pending", "running", "success", "failed", name="agent_step_status_enum"),
        default="pending",
        nullable=False,
    )
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text, default="")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AgentLog(id={self.id}, game_id={self.game_id}, step='{self.step_name}', status='{self.status}')>"
