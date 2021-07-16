from sqlalchemy import Column, JSON, Integer, Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config
import enum


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Game(Base):
    __tablename__ = "games"

    class Players(enum.Enum):
        BLACK = -1
        WHITE = 1

    id = Column(Integer, primary_key=True, index=True)
    board = Column(JSON, nullable=False)
    winner = Column(Enum(Players), nullable=True)


Base.metadata.create_all(bind=engine)  # noqa
