import os
from pathlib import Path

class Config:
    SECRET_KEY = 'your-random-secret-key'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = None  # No primary database; all are binds
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dynamically detect .db and .sqlite files in /data
    BASE_DIR = Path('/data/data/com.termux/files/home/lotto/sqlite_manager')
    DATA_DIR = BASE_DIR / 'data'
    SQLALCHEMY_BINDS = {}
    
    for db_file in DATA_DIR.glob('*.db'):
        bind_key = db_file.stem  # e.g., 'states' for 'states.db'
        SQLALCHEMY_BINDS[bind_key] = f'sqlite:///{db_file}'
    for db_file in DATA_DIR.glob('*.sqlite'):
        bind_key = db_file.stem
        SQLALCHEMY_BINDS[bind_key] = f'sqlite:///{db_file}'