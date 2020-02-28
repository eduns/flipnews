APP_NAME = 'FlipNews'

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:edugenix@localhost:5432/flipnews'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'edugenix'

UPLOADED_IMAGES_DEST = 'app/news/static/images'
