# Web Server

Django backend server with MySQL, Redis, Celery, and Aliyun OSS integration.

## Environment Variables

### Django Core

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-dev-key-must-change` |
| `DJANGO_SETTINGS_MODULE` | Settings module path | `app.settings.aliyun` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `example.com,api.example.com` |

### Database

| Variable | Description | Example |
|----------|-------------|---------|
| `WEB_DBNAME` | Database name | `genprime_db` |
| `WEB_DBUSER` | Database user | `db_user` |
| `WEB_DBPASS` | Database password | `db_password` |
| `WEB_DBHOST` | Database host | `localhost` |
| `WEB_DBPORT` | Database port | `3306` |

### Redis

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_CACHE_URL` | Redis URL for cache | `redis://localhost:6379/0` |
| `REDIS_SESSION_URL` | Redis URL for sessions | `redis://localhost:6379/1` |

### Celery

| Variable | Description | Example |
|----------|-------------|---------|
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/2` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://localhost:6379/3` |

### Aliyun OSS

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ALIYUN_OSS_ACCESS_KEY_ID` | RAM AccessKey ID | `LTAI5t...` | Yes |
| `ALIYUN_OSS_ACCESS_KEY_SECRET` | RAM AccessKey Secret | `xxxx...` | Yes |
| `ALIYUN_OSS_BUCKET_NAME` | Bucket name | `my-bucket` | Yes |
| `ALIYUN_OSS_REGION` | Bucket region | `cn-hangzhou` | Yes |
| `ALIYUN_OSS_INTERNAL_ENDPOINT` | Internal endpoint (optional) | `my-bucket.oss-cn-hangzhou-internal.aliyuncs.com` | No |
| `ALIYUN_OSS_PUBLIC_URL_DOMAIN` | Public URL domain | `my-bucket.oss-cn-hangzhou.aliyuncs.com` | Yes |

**Note:**
- `Storage.url()` returns public URL (for browser access)
- `Storage.path()` returns internal endpoint URL (for server-side processing, reduces bandwidth costs)
- If internal endpoint is not configured, `path()` falls back to public URL

## GitHub Actions Secrets

This repository uses GitHub Actions for CI/CD. The following secrets must be configured in your repository settings:

### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `ALIYUN_REGISTRY` | Aliyun Container Registry address | `registry.cn-hangzhou.aliyuncs.com` |
| `ALIYUN_REGISTRY_USER` | Container Registry username | `your-username` |
| `ALIYUN_REGISTRY_PWD` | Container Registry password | `your-password` |
| `ALIYUN_NAMESPACE` | Container Registry namespace | `your-namespace` |
| `ALIYUN_AK` | Aliyun Access Key ID | `LTAI5t...` |
| `ALIYUN_SK` | Aliyun Access Key Secret | `xxxx...` |

### How to Configure

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the table above

### Workflows Using These Secrets

- **`.github/workflows/deploy-aluyun-production.yml`** - Deploys to Aliyun SAE (triggered on `production` branch pushes)
- **`.github/workflows/pr-check.yml`** - PR checks (no secrets required)
- **`.github/workflows/release.yml`** - Creates PR from `main` to `production` (no secrets required)
