import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'doudettecorp@gmail.com'
    MAIL_PASSWORD = 'd0udette'
    APP_MAIL_SUBJECT_PREFIX = 'rss_tweet'
    APP_MAIL_SENDER = 'doudettecorp@gmail.com'
    FLASKY_ADMIN = 'j_fiot@hotmail.com'
    # Twitter homsee_fr	homsee_fr // ouinner75
    KEY_CONSUMER = 'rijY1OmtJCnnSDj6KbU1ZnKN7'
    CONSUMER_SECRET = 'HnwRyqruTEUzu5KLCJPcNcjuBDQ9E8Tt6qLcMl2PM2GjrIj5zJ'
    ACCESS_TOKEN = '1361814511-JLIrvRqjUqHfkGFXWzlVwZ3DWs2zOlGpVfzmhD4'
    ACCESS_TOKEN_SECRET = 'aMrrdU0Etb6cR4HTjnX6q8Cv2pyVyQKF4euHNMN20V3TH'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://rss_tweet:rss_tweet123@127.0.0.1:3306/rss_tweet'

# class ProductionConfig(Config):
#     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://userSQL:passw_userSQL@hostSQL:portSQL/baseSQL'

config = {
    'development': DevelopmentConfig,
    # 'production': ProductionConfig,
    'default': DevelopmentConfig
}
