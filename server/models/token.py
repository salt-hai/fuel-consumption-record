from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    last_used_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="tokens")
