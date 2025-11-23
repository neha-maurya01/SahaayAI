from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class LiteracyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Channel(str, enum.Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    WEB = "web"

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Domain(str, enum.Enum):
    HEALTH = "health"
    AGRICULTURE = "agriculture"
    FINANCE = "finance"
    EDUCATION = "education"
    GOVERNMENT_SCHEMES = "government_schemes"
    CLIMATE = "climate"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number_encrypted = Column(String, unique=True, index=True)
    preferred_language = Column(String, default=settings.DEFAULT_LANGUAGE)
    literacy_level = Column(Enum(LiteracyLevel), default=LiteracyLevel.MEDIUM)
    location_district = Column(String, nullable=True)
    location_state = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    consent_given = Column(Integer, default=0)  # Boolean as int for SQLite
    
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel = Column(Enum(Channel))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    action_plans = relationship("ActionPlan", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(Enum(MessageRole))
    content_encrypted = Column(Text)
    language = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    conversation = relationship("Conversation", back_populates="messages")

class ActionPlan(Base):
    __tablename__ = "action_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    domain = Column(Enum(Domain))
    steps = Column(JSON)  # Array of step objects
    documents_required = Column(JSON)  # Array of document names
    eligibility_status = Column(String, nullable=True)
    risk_alerts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="action_plans")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(Enum(Domain))
    category = Column(String)
    title = Column(String)
    content = Column(JSON)  # Multilingual content
    keywords = Column(Text)  # Searchable keywords
    language = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
