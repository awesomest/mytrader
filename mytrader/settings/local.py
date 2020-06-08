"""local.py"""
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "ekfGJe-AxVXk*h-xoRc8i.QfYzvbx8CV.Fa4_7b3LrDuM4VmLx"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

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
        "PORT": "4306",
        "NAME": "test",
        "USER": "eraise",
        "PASSWORD": "eraise",
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'",},
    }
}
