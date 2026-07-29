from .base import *
from cashfree_pg.api_client import Cashfree

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "192.168.1.16",
    "localhost"
]

CASHFREE_CLIENT_ID = env("CASHFREE_CLIENT_ID")
CASHFREE_CLIENT_SECRET_KEY = env("CASHFREE_CLIENT_SECRET_KEY")
CASHFREE_WEBHOOK_SECRET = env("CASHFREE_WEBHOOK_SECRET")

_cf_env_str = str(env("CASHFREE_ENVIRONMENT", default="SANDBOX")).lower()
if "sandbox" in _cf_env_str:
    CASHFREE_ENVIRONMENT = Cashfree.SANDBOX
else:
    CASHFREE_ENVIRONMENT = Cashfree.PRODUCTION

JAVASCRIPT_ENV = env("JAVASCRIPT_ENV")