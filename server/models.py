from sqlalchemy import Column, Integer, String, Double
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    usertype = Column(String, index=True)
    userInfoName = Column(String, index=True)
    userInfoSurname = Column(String, index=True)
    userInfoAvatar = Column(String, index=True)
    userStatProjects = Column(Integer, index=True)
    userStatTasks = Column(Integer, index=True)
    userStatOntime = Column(Double, index=True)
    userCurrentEarnings = Column(Integer, index=True)
    userAllTimeEarnings = Column(Integer, index=True)

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    textMessage = Column(String, index=True)
    fromWho = Column(String, index=True)
    toWho = Column(String, index=True)
    timeMessage = Column(String, index=True)

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    owner = Column(String, index=True)
    file_type = Column(String, index=True)
    url = Column(String)
    uploaded_at = Column(String)

