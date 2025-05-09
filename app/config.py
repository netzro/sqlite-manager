class Config:
    SECRET_KEY = 'your-random-secret-key'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////data/data/com.termux/files/home/scripts/states.db'
    SQLALCHEMY_BINDS = {
        'past_results': 'sqlite:////data/data/com.termux/files/home/lotto/past_results.db'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False