from typing import Optional
from uuid import uuid4
import shutil
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from fastapi.staticfiles import StaticFiles
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    Body,
    Depends,
    HTTPException,
)


# DataBase and sqlalchemy setup
SQLALCHEMY_DATABASE_URL = (
    "sqlite:///./sql_app.db"  # sqlite should not be used in production
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True)


class ApkFile(Base):
    __tablename__ = "apkfiles"

    id = Column(Integer, primary_key=True)
    uid = Column(
        String(256), nullable=False
    )  # it is also the filename in static folder
    package_name = Column(String(256), nullable=False)
    version = Column(String(10), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="apkfiles", lazy=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


# FastAPI Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/user/{user_id}/files/")
async def user_files(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"user {user_id} Not found",
        )
    user_files = (
        db.query(ApkFile).filter(ApkFile.user_id == user.id).all()
    )  # not for production
    return {
        "user_id": user.id,
        "username": user.username,
        "files": [
            {
                "id": apk.id,
                "uid": apk.uid,
                "package_name": apk.package_name,
                "version": apk.version,
                "url": f"127.0.0.1:8000/static/{apk.uid}.apk",
            }
            for apk in user_files
        ],
    }


@app.post("/user/")
async def new_user(
    username: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"id": user.id, "username": user.username}
    raise HTTPException(
        status_code=400,
        detail=f"user {username} already exists",
    )


@app.post("/getuid/")
async def check_existing_file(
    package_name: str = Body(...),
    version: str = Body(...),
    db: Session = Depends(get_db),
):
    apk = (
        db.query(ApkFile)
        .filter(
            ApkFile.package_name == package_name,
            ApkFile.version == version,
        )
        .first()
    )
    if apk is None:
        uuid = f"{package_name}-{version}-{uuid4()}"
        return {
            "uid": uuid,
            "uploaded": False,
        }
    return {
        "uploaded": True,
        "id": apk.id,
        "uid": apk.uid,
        "package_name": apk.package_name,
        "version": apk.version,
    }


@app.post("/upload/")
async def create_upload_file(
    uid: str = Form(...),
    file: Optional[UploadFile] = File(None),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"user {user_id} Not found",
        )
    package_name, version, *_ = uid.split("-")
    apk = (
        db.query(ApkFile)
        .filter(
            ApkFile.uid == uid,
            ApkFile.user_id == user_id,
        )
        .first()
    )
    if apk:
        raise HTTPException(
            status_code=400, detail=f"file already uploaded for user {user_id}"
        )
    if not file and not apk:
        raise HTTPException(status_code=400, detail="file not found! upload a file")
    if file:
        if not file.filename.endswith(".apk"):
            raise HTTPException(status_code=400, detail="its not a .apk file")
        path = f"static/{uid}.apk"
        if not os.path.isfile(path):
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            raise HTTPException(status_code=400, detail="file already exists")

    apk = ApkFile(
        uid=uid,
        package_name=package_name,
        version=version,
        user_id=user.id,
    )
    db.add(apk)
    db.commit()
    db.refresh(apk)

    return {
        "id": apk.id,
        "package_name": apk.package_name,
        "version": apk.version,
        "user_id": apk.user_id,
    }


@app.get("/")
def main():
    return {"status": "online"}
