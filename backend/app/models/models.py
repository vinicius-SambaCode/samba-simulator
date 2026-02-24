from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

class Discipline(Base):
    __tablename__ = "disciplines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # Adicione outros campos conforme sua necessidade
