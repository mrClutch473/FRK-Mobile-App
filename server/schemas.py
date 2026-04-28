from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    usertype: str
    userInfoName: str
    userInfoSurname: str
    userInfoAvatar: str
    userStatProjects: int
    userStatTasks: int
    userStatOntime: float
    userCurrentEarnings: int
    userAllTimeEarnings: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdatedData(BaseModel):
    email: str
    username: str
    password: str
    userInfoName: str
    userInfoSurname: str

class MessageCreate(BaseModel):
    textMessage: str
    fromWho: str
    toWho: str
    timeMessage: str

class MediaFileOut(BaseModel):
    filename: str
    owner: str
    file_type: str
    url: str
    uploaded_at: str