import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///forensic_audio.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "audio")
    ALLOWED_EXTENSIONS = {"wav", "mp3", "flac"}
