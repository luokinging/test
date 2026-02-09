from urllib.parse import urljoin

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

import alibabacloud_oss_v2 as oss
from alibabacloud_oss_v2.models import (
    PutObjectRequest,
    GetObjectRequest,
    DeleteObjectRequest,
    ListObjectsV2Request,
)
from alibabacloud_oss_v2.credentials import StaticCredentialsProvider


class AliyunOSSFile:
    def __init__(self, body):
        self.body = body
        self._read_done = False

    def read(self):
        if not self._read_done:
            self._read_done = True
            return self.body.read()
        return b""

    def close(self):
        if hasattr(self.body, "close"):
            self.body.close()


@deconstructible
class AliyunOSSV2Storage(Storage):
    def __init__(self, **kwargs):
        self.options = kwargs
        self._validate_required_options()
        self._client = None

        self.bucket_name = self.options["bucket_name"]
        self.region = self.options["region"]
        self.endpoint = self.options.get("endpoint")
        self.public_url_domain = self.options["public_url_domain"]
        self.prefix = self.options.get("prefix", "").rstrip("/")

    def _validate_required_options(self):
        required_options = [
            "access_key_id",
            "access_key_secret",
            "bucket_name",
            "region",
            "public_url_domain",
        ]
        missing_options = [
            opt
            for opt in required_options
            if opt not in self.options or not self.options[opt]
        ]

        if missing_options:
            raise ImproperlyConfigured(
                f"Missing required Aliyun OSS options: {', '.join(missing_options)}"
            )

    @property
    def client(self):
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self):
        credentials_provider = StaticCredentialsProvider(
            access_key_id=self.options["access_key_id"],
            access_key_secret=self.options["access_key_secret"],
        )

        cfg = oss.config.load_default()
        cfg.credentials_provider = credentials_provider
        cfg.region = self.region

        if self.endpoint:
            cfg.endpoint = self.endpoint

        return oss.Client(cfg)

    def _get_object_key(self, name):
        if self.prefix:
            return f"{self.prefix}/{name}"
        return name

    def _open(self, name, mode="rb"):
        if mode != "rb":
            raise ValueError("Only read-binary mode is supported")

        key = self._get_object_key(name)
        request = GetObjectRequest(bucket=self.bucket_name, key=key)
        result = self.client.get_object(request)

        return AliyunOSSFile(result.body)

    def _save(self, name, content):
        key = self._get_object_key(name)

        if hasattr(content, "read"):
            content = content.read()

        content_type = None
        if hasattr(content, "content_type"):
            content_type = content.content_type

        request = PutObjectRequest(
            bucket=self.bucket_name,
            key=key,
            body=content,
        )

        if content_type:
            request.content_type = content_type

        self.client.put_object(request)
        return name

    def delete(self, name):
        key = self._get_object_key(name)
        request = DeleteObjectRequest(bucket=self.bucket_name, key=key)
        self.client.delete_object(request)

    def exists(self, name):
        try:
            key = self._get_object_key(name)
            request = GetObjectRequest(bucket=self.bucket_name, key=key)
            self.client.get_object(request)
            return True
        except Exception:
            return False

    def listdir(self, path):
        prefix = self._get_object_key(path)
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        request = ListObjectsV2Request(
            bucket=self.bucket_name,
            prefix=prefix,
            delimiter="/",
            max_keys=1000,
        )

        paginator = self.client.list_objects_v2_paginator()
        directories = set()
        files = []

        for page in paginator.iter_page(request):
            if page.common_prefixes:
                for prefix_obj in page.common_prefixes:
                    dir_name = prefix_obj.prefix.rstrip("/")
                    if "/" in dir_name:
                        dir_name = dir_name.split("/")[-1]
                    directories.add(dir_name)

            if page.contents:
                for obj in page.contents:
                    file_name = obj.key[len(prefix) :] if prefix else obj.key
                    if file_name and "/" not in file_name:
                        files.append(file_name)

        return list(directories), files

    def size(self, name):
        key = self._get_object_key(name)
        request = ListObjectsV2Request(
            bucket=self.bucket_name,
            prefix=key,
            max_keys=1,
        )
        result = self.client.list_objects_v2(request)
        if result.contents:
            return result.contents[0].size
        return 0

    def url(self, name):
        key = self._get_object_key(name)
        return urljoin(f"https://{self.public_url_domain}/", key)

    def get_accessed_time(self, name):
        return self.get_modified_time(name)

    def get_created_time(self, name):
        return self.get_modified_time(name)

    def get_modified_time(self, name):
        key = self._get_object_key(name)
        request = ListObjectsV2Request(
            bucket=self.bucket_name,
            prefix=key,
            max_keys=1,
        )
        result = self.client.list_objects_v2(request)
        if result.contents:
            return result.contents[0].last_modified
        return None

    def path(self, name):
        if self.endpoint:
            key = self._get_object_key(name)
            return urljoin(f"https://{self.endpoint}/", key)
        return self.url(name)
