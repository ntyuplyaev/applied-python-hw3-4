from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArchivedLink(Base):
    __tablename__ = "archived_links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, index=True)
    custom_alias = Column(String, index=True)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    clicks = Column(Integer)
    last_accessed = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    archived_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Таблица для связи многие-ко-многим
link_project_association = Table(
    'link_project_association',
    Base.metadata,
    Column('link_id', Integer, ForeignKey('links.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True)
    custom_alias = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    clicks = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    projects = relationship("Project", secondary=link_project_association, backref="links")
