class Config:
    # database configurations
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rootpassword@db/PickADateDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # debug mode
    DEBUG = True