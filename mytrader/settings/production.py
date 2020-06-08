import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["mytrader-279617.appspot.com", "mytrader-279617.df.r.appspot.com"]

# Running on production App Engine, so connect to Google Cloud SQL using
# the unix socket at /cloudsql/<your-cloudsql-connection string>
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.mysql",
    "HOST": os.getenv("DB_HOST"),
    "NAME": os.getenv("DB_NAME"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "OPTIONS": {
      "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    },
  }
}
