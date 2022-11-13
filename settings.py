import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_TOKEN")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "db",
    "django_async_orm",
    "django_extensions",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES["default"].update(db_from_env)

TIME_ZONE = "Asia/Seoul"
USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
