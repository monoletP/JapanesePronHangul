# Google Cloud Run 배포 가이드

## 사전 준비

1. Google Cloud 프로젝트 생성
2. gcloud CLI 설치 및 로그인
3. Cloud Run API 활성화
4. Artifact Registry API 활성화

## 배포 단계

### 1. gcloud 설정

```bash
# 프로젝트 ID 설정
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 리전 설정 (서울: asia-northeast3)
export REGION="asia-northeast3"
```

### 2. Artifact Registry 생성 (처음 한 번만)

```bash
gcloud artifacts repositories create japanese-pron \
    --repository-format=docker \
    --location=$REGION \
    --description="Japanese to Hangul Converter"
```

### 3. Docker 이미지 빌드 및 푸시

```bash
# Docker 이미지 빌드
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/japanese-pron/app

# 또는 로컬 빌드 후 푸시
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/japanese-pron/app .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/japanese-pron/app
```

### 4. Cloud Run 배포

```bash
gcloud run deploy japanese-pron \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/japanese-pron/app \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080
```

### 5. URL 확인

배포 완료 후 제공되는 URL로 접속:
```
https://japanese-pron-[hash]-an.a.run.app
```

## 업데이트

```bash
# 코드 수정 후
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/japanese-pron/app

# 자동으로 새 버전 배포됨
```

## 비용

- **무료 티어**: 월 200만 요청, 36만 GB-초, 18만 vCPU-초
- **초과 시**: 
  - 요청당 $0.40/백만
  - CPU: $0.00002400/vCPU-초
  - 메모리: $0.00000250/GiB-초

## 도메인 연결 (선택사항)

```bash
gcloud run domain-mappings create \
    --service japanese-pron \
    --domain your-domain.com \
    --region $REGION
```

## 환경 변수 설정 (필요시)

```bash
gcloud run services update japanese-pron \
    --update-env-vars KEY=VALUE \
    --region $REGION
```

## 로그 확인

```bash
gcloud run logs read japanese-pron --region $REGION
```
