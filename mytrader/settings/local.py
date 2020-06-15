"""local.py"""
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "ekfGJe-AxVXk*h-xoRc8i.QfYzvbx8CV.Fa4_7b3LrDuM4VmLx"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Security
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_SSL_REDIRECT = True
# SECURE_REFERRER_POLICY = "same-origin"
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Running locally so connect to either a local MySQL instance or connect to
# Cloud SQL via the proxy. To start the proxy via command line:
#
#     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
#
# See https://cloud.google.com/sql/docs/mysql-connect-proxy
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "127.0.0.1",
        "NAME": "test",
        "USER": "eraise",
        "PASSWORD": "eraise",
        "PORT": "4306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'",  # pylint: disable=line-too-long
        },
    }
}
