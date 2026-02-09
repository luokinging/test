from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


DATABASES = {
    "default": {
        **DATABASES["default"],
        "CONN_MAX_AGE": 600,
        "CONN_HEALTH_CHECKS": True,
    }
}


ALIYUN_OSS_CONFIG = {
    "access_key_id": os.environ["ALIYUN_OSS_ACCESS_KEY_ID"],
    "access_key_secret": os.environ["ALIYUN_OSS_ACCESS_KEY_SECRET"],
    "bucket_name": os.environ["ALIYUN_OSS_BUCKET_NAME"],
    "region": os.environ["ALIYUN_OSS_REGION"],
    "endpoint": os.environ.get("ALIYUN_OSS_INTERNAL_ENDPOINT"),
    "public_url_domain": os.environ["ALIYUN_OSS_PUBLIC_URL_DOMAIN"],
}
ALIYUN_OSS_CONFIG = {k: v for k, v in ALIYUN_OSS_CONFIG.items() if v is not None}

STORAGES = {
    "default": {
        "BACKEND": "app.storage.aliyun.AliyunOSSV2Storage",
        "OPTIONS": {**ALIYUN_OSS_CONFIG, "prefix": "default"},
    },
    "user_upload": {
        "BACKEND": "app.storage.aliyun.AliyunOSSV2Storage",
        "OPTIONS": {**ALIYUN_OSS_CONFIG, "prefix": "user_upload"},
    },
    "generated": {
        "BACKEND": "app.storage.aliyun.AliyunOSSV2Storage",
        "OPTIONS": {**ALIYUN_OSS_CONFIG, "prefix": "generated"},
    },
    "staticfiles": {
        "BACKEND": "app.storage.aliyun.AliyunOSSV2Storage",
        "OPTIONS": {**ALIYUN_OSS_CONFIG, "prefix": "django_static"},
    },
}
