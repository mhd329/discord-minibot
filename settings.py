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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3+xlx91i!7$^by%*-39cotq5gddtid%+$@4u1t@2gld3s6brr#"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "db",
    "django_extensions",
    "django_async_orm",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

TIME_ZONE = "Asia/Seoul"
USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
