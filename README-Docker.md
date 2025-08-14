# Back Note - Docker Deployment Guide

이 문서는 Back Note 애플리케이션을 Docker를 사용하여 배포하는 방법을 설명합니다.

## 📋 요구사항

- Docker (20.10 이상)
- Docker Compose (2.0 이상)
- 최소 2GB RAM
- 최소 5GB 디스크 공간

## 🚀 빠른 시작

### 1. 개발 환경 시작

```bash
# 스크립트 사용 (권장)
./scripts/start.sh dev

# 또는 직접 Docker Compose 사용
docker-compose up --build -d
```

### 2. 프로덕션 환경 시작

```bash
# 스크립트 사용 (권장)
./scripts/start.sh prod

# 또는 직접 Docker Compose 사용
docker-compose -f docker-compose.prod.yml up --build -d
```

### 3. 애플리케이션 접속

- **개발 환경**: http://localhost:8501
- **프로덕션 환경**: https://localhost

## 📁 프로젝트 구조

```
back-note/
├── Dockerfile                 # Docker 이미지 정의
├── docker-compose.yml         # 개발 환경 설정
├── docker-compose.prod.yml    # 프로덕션 환경 설정
├── .dockerignore             # Docker 빌드 제외 파일
├── nginx.conf                # Nginx 설정 (프로덕션)
├── scripts/
│   └── start.sh              # 배포 스크립트
├── data/                     # 데이터베이스 파일 (자동 생성)
├── logs/                     # 로그 파일 (자동 생성)
└── ssl/                      # SSL 인증서 (자동 생성)
```

## 🛠️ 관리 명령어

### 스크립트 사용 (권장)

```bash
# 개발 환경 시작
./scripts/start.sh dev

# 프로덕션 환경 시작
./scripts/start.sh prod

# 애플리케이션 중지
./scripts/start.sh stop

# 로그 확인
./scripts/start.sh logs

# 상태 확인
./scripts/start.sh status

# 전체 정리 (컨테이너, 이미지, 볼륨 삭제)
./scripts/start.sh clean

# 도움말
./scripts/start.sh help
```

### 직접 Docker 명령어 사용

```bash
# 개발 환경
docker-compose up --build -d
docker-compose down

# 프로덕션 환경
docker-compose -f docker-compose.prod.yml up --build -d
docker-compose -f docker-compose.prod.yml down

# 로그 확인
docker-compose logs -f
docker-compose -f docker-compose.prod.yml logs -f

# 컨테이너 상태 확인
docker-compose ps
docker-compose -f docker-compose.prod.yml ps
```

## 🔧 환경 설정

### 환경 변수

애플리케이션은 다음 환경 변수를 지원합니다:

```bash
# Streamlit 설정
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Python 설정
PYTHONPATH=/app
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

### 볼륨 마운트

다음 디렉토리가 호스트에 마운트됩니다:

- `./data:/app/data` - 데이터베이스 파일
- `./logs:/app/logs` - 로그 파일
- `./ssl:/app/ssl` - SSL 인증서 (프로덕션)

## 🔒 보안 설정

### 프로덕션 환경

프로덕션 환경에서는 다음 보안 기능이 활성화됩니다:

- **XSRF 보호**: `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true`
- **업로드 크기 제한**: `STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200`
- **사용 통계 비활성화**: `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`
- **리소스 제한**: 메모리 1GB, CPU 0.5 코어
- **보안 옵션**: `no-new-privileges:true`
- **Nginx 리버스 프록시**: SSL 종료, 압축, 보안 헤더

### SSL 인증서

개발 환경에서는 자동으로 자체 서명된 SSL 인증서가 생성됩니다.
프로덕션 환경에서는 실제 SSL 인증서를 사용하세요:

```bash
# SSL 인증서 파일을 ssl/ 디렉토리에 배치
ssl/
├── cert.pem    # SSL 인증서
└── key.pem     # SSL 개인키
```

## 📊 모니터링

### 헬스 체크

애플리케이션은 다음 엔드포인트로 헬스 체크를 제공합니다:

- **Streamlit**: `http://localhost:8501/_stcore/health`
- **Nginx**: `https://localhost/health`

### 로그 확인

```bash
# 애플리케이션 로그
docker-compose logs -f back-note

# Nginx 로그 (프로덕션)
docker-compose -f docker-compose.prod.yml logs -f nginx

# 모든 로그
docker-compose logs -f
```

## 🔄 업데이트

애플리케이션을 업데이트하려면:

```bash
# 1. 애플리케이션 중지
./scripts/start.sh stop

# 2. 최신 코드 가져오기
git pull origin main

# 3. 새 이미지 빌드 및 시작
./scripts/start.sh dev  # 또는 prod
```

## 🐛 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   lsof -i :8501
   
   # 다른 포트 사용
   docker-compose up -d -p 8502:8501
   ```

2. **권한 문제**
   ```bash
   # 스크립트 실행 권한 부여
   chmod +x scripts/start.sh
   
   # Docker 권한 확인
   docker info
   ```

3. **메모리 부족**
   ```bash
   # Docker 리소스 확인
   docker stats
   
   # 불필요한 컨테이너 정리
   docker system prune -f
   ```

4. **데이터베이스 문제**
   ```bash
   # 데이터베이스 파일 확인
   ls -la data/
   
   # 백업 생성
   cp data/my_app_database.db data/backup_$(date +%Y%m%d_%H%M%S).db
   ```

### 로그 분석

```bash
# 에러 로그만 확인
docker-compose logs | grep ERROR

# 최근 로그 확인
docker-compose logs --tail=100

# 특정 시간 이후 로그
docker-compose logs --since="2024-01-01T00:00:00"
```

## 📈 성능 최적화

### 리소스 제한

프로덕션 환경에서는 리소스 제한이 설정됩니다:

```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### Nginx 최적화

- **Gzip 압축**: 텍스트 파일 압축
- **캐싱**: 정적 파일 캐싱
- **Rate Limiting**: API 요청 제한
- **보안 헤더**: XSS, CSRF 보호

## 🔧 커스터마이징

### Dockerfile 수정

애플리케이션에 추가 패키지가 필요한 경우:

```dockerfile
# Dockerfile에 추가
RUN apt-get update && apt-get install -y \
    your-package-name \
    && rm -rf /var/lib/apt/lists/*
```

### Nginx 설정 수정

`nginx.conf` 파일을 수정하여 추가 설정을 적용할 수 있습니다.

### 환경별 설정

다른 환경을 위한 추가 docker-compose 파일을 생성할 수 있습니다:

```bash
docker-compose.staging.yml
docker-compose.test.yml
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. Docker 및 Docker Compose 버전
2. 시스템 리소스 (메모리, 디스크)
3. 네트워크 연결
4. 방화벽 설정
5. 로그 파일

추가 지원이 필요한 경우 프로젝트 이슈를 생성하거나 개발팀에 문의하세요.
