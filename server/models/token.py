from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Token(Base):
    """
    Authentication token storage model.

    This model stores hashed authentication tokens for user sessions.
    The actual token values are never stored in plaintext - only SHA256 hashes.

    Attributes:
        id: Primary key, auto-incrementing identifier
        user_id: Foreign key reference to the user who owns this token
        token_hash: SHA256 hash of the authentication token (unique, indexed for lookups)
        created_at: Timestamp when the token was created/issued
        last_used_at: Timestamp of the most recent authentication using this token

    Usage:
        - Tokens are generated when users log in
        - Tokens are validated by comparing request token hashes against stored hashes
        - Tokens can be revoked by deleting the corresponding database record
    """
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    last_used_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="tokens")
