from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import User, Messages, MediaFile
from schemas import UserCreate, UserLogin, MessageCreate, MediaFileOut, UserUpdatedData
from auth import hash_password, verify_password

from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
import shutil, uuid
from pathlib import Path
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="uploads"), name="static")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test")
def test():
    return {
        "message": "All work"
    }

@app.post("/sendMessage")
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    new_message = Messages(
        textMessage=message.textMessage,
        fromWho=message.fromWho,
        toWho=message.toWho,
        timeMessage=message.timeMessage
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return {
        "response": 1,
        "message": "Message sent"
    }

@app.get("/getHistory")
def get_history(fromWho: str, toWho: str, db: Session = Depends(get_db)):
    messages = db.query(Messages).filter(
        ((Messages.fromWho == fromWho) & (Messages.toWho == toWho)) |
        ((Messages.fromWho == toWho) & (Messages.toWho == fromWho))
    ).all()
    return {
        "response": 1,
        "messages": [
            {
                "textMessage": m.textMessage,
                "fromWho": m.fromWho,
                "toWho": m.toWho,
                "timeMessage": m.timeMessage
            }
            for m in messages
        ]
    }

@app.get("/getMessages")
def get_messages(currentUser: str, db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        if user.username == currentUser:
            continue

        messages = db.query(Messages).filter(
            ((Messages.fromWho == currentUser) & (Messages.toWho == user.username)) |
            ((Messages.fromWho == user.username) & (Messages.toWho == currentUser))
        ).all()

        history = [
            {
                "textMessage": m.textMessage,
                "fromWho": m.fromWho,
                "toWho": m.toWho,
                "timeMessage": m.timeMessage
            }
            for m in messages
        ]

        result.append({
            "username": user.username,
            "userInfoName": user.userInfoName,
            "userInfoAvatar": user.userInfoAvatar,
            "messageHistory": history
        })

    return {
        "response": 1,
        "users": result
    }

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        return {
            "response": -21,
            "message": "Not find user with this data",
            "user_id": 0
        }

    if not verify_password(user.password, db_user.hashed_password):
        return {
            "response": -22,
            "message": "Incorrect password",
            "user_id": 0
        }
    else:
        return {
            "response": 1,
            "message": "Login successful",
            "user_id": db_user.id,
            "email": db_user.email,
            "hashed_password": db_user.hashed_password,
            "usertype": db_user.usertype,
            "userInfoName": db_user.userInfoName,
            "userInfoSurname": db_user.userInfoSurname,
            "userInfoAvatar": db_user.userInfoAvatar
        }

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return {
            "response": -11,
            "message": "User with same mail already exists",
            "user_id": 0
        }

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        return {
            "response": -12,
            "message": "User with same username already exists",
            "user_id": 0
        }

    # создание пользователя
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        usertype=user.usertype,
        userInfoName=user.userInfoName,
        userInfoSurname = user.userInfoSurname,
        userInfoAvatar = user.userInfoAvatar
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "response": 1,
        "message": " New User created",
        "user_id": new_user.id
    }

@app.post("/updateUserType")
def update_user_type(user_email: str, new_user_type: str, db: Session = Depends(get_db)):
    current_user = db.query(User).filter(User.email == user_email).first()
    if current_user:
        current_user.usertype = new_user_type
        db.commit()

        return {
            "response": 1,
            "message": "New User Type correctly uploaded",
        }
    else:
        return {
            "response": -1,
            "message": "Fail to update User Type, can't find correct user",
        }

@app.post("/updateUserData")
def update_user_data(last_email: str, new_user_data: UserUpdatedData, db: Session = Depends(get_db)):
    current_user = db.query(User).filter(User.email == last_email).first()
    if current_user:
        if new_user_data.email != last_email:
            current_user.email = new_user_data.email
        current_user.username = new_user_data.username
        current_user.userInfoName = new_user_data.userInfoName
        current_user.userInfoSurname = new_user_data.userInfoSurname

        if new_user_data.password.strip():
            current_user.hashed_password = hash_password(new_user_data.password)

        db.commit()

        return {
            "response": 1,
            "message": "New User data correctly uploaded",
        }
    else:
        print(f"Updating user: name={new_user_data.userInfoName}, surname={new_user_data.userInfoSurname}", flush=True)
        return {
            "response": -1,
            "message": "Fail to update User Data, can't find correct user",
        }

@app.post("/updateAvatar")
def update_avatar(username: str, new_avatar_url: str, db: Session = Depends(get_db)):

    current_user = db.query(User).filter(User.username == username).first()
    if current_user:
        current_user.userInfoAvatar = new_avatar_url
        db.commit()

        return {
            "response": 1,
            "message": "New UserInfoAvatar uploaded",
        }
    else:
        return {
            "response": -1,
            "message": "Fail to update UserInfoAvatar, can't find correct user",
        }

@app.post("/uploadFile")
async def upload_file(
    owner: str,
    file_type: str,               # "avatar", "document" и т.д.
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Создаём подпапку под тип файла
    folder = UPLOAD_DIR / file_type
    folder.mkdir(parents=True, exist_ok=True)

    # Уникальное имя чтобы не было коллизий
    ext = file.filename.split(".")[-1]
    filename = f"{owner}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = folder / filename

    # Сохраняем на диск
    with filepath.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"http://45.150.36.29:8000/static/{file_type}/{filename}"

    # Сохраняем метаданные в БД
    media = MediaFile(
        filename=filename,
        owner=owner,
        file_type=file_type,
        url=url,
        uploaded_at=datetime.now().isoformat()
    )
    db.add(media)
    db.commit()

    return {"response": 1, "url": url, "filename": filename}

@app.get("/getFile/{filename}", response_model=MediaFileOut)
def get_file(filename: str, db: Session = Depends(get_db)):
    media = db.query(MediaFile).filter(MediaFile.filename == filename).first()

    if not media:
        return {"response": -1, "message": "File not found"}

    return media
