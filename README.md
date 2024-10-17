# 🚀 AI FastAPI 서버

## 📄 시작하기

### 🖥️ 로컬
1. **Docker 이미지를 빌드합니다:**
    ```bash
    docker build -t ai-fastapi-api-v-c:latest -f dockerfile .
    ```
2. **Docker 컨테이너를 실행합니다:**
    ```bash
    docker run -d -p 8003:8001 --gpus all --name ai-fastapi-api-v-c \
    -e HASH_KEY=<YOUR_HASH_KEY> \
    -e REDIS_SENTINEL_PASSWORD=<YOUR_REDIS_PASSWORD> \
    -e REDIS_SENTINEL_NODE1=<YOUR_REDIS_NODE1> \
    -e REDIS_SENTINEL_NODE2=<YOUR_REDIS_NODE2> \
    -e REDIS_SENTINEL_NODE3=<YOUR_REDIS_NODE3> \
    -e USE_CUDA=1 \
    ai-fastapi-api-v-c
    ```

### ☁️ ECR
1. 개인 브랜치를 만들고 `main`으로 PR 주시면, 관리자가 ECR + Lambda 배포를 진행해 드립니다.

---

## 📡 API 사용 방법

### 📝 용언 추출 API
- **엔드포인트**: `/predicate`
- **메서드**: `POST`
- **설명**: MeCab을 사용하여 한국어 텍스트를 분석합니다.
- **요청 바디**:
    ```json
    {
      "text": "진짜 개재밌다 ㅋㅋㅋ"
    }
    ```

- **Curl 명령어 예제**:
    - 로컬:
        ```bash
        curl -X POST "http://127.0.0.1:8003/nlp/predicate" -H "Content-Type: application/json" -d '{"keyword":"손흥민", "related":"토트넘"}'
        ```
    - AWS:
        ```bash
        curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/predicate" -H "Content-Type: application/json" -d '{"keyword":"손흥민", "related":"토트넘"}'
        ```

- **성공 응답**:
    ```json
    {"code":200,"message":"success","data":[{"keyword":"폭발하다","count":126},{"keyword":"밝히다","count":67},{"keyword":"요구하다","count":65},{"keyword":"요청하다","count":64}]}
    ```

### 🔗 연관어 API
- **엔드포인트**: `/related`
- **메서드**: `POST`
- **설명**: 최신 데이터 및 Word2vec 알고리즘을 기반으로 연관어를 분석합니다.
- **요청 바디**:
    ```json
    {
      "text": "손흥민"
    }
    ```

- **Curl 명령어 예제**:
    - 로컬:
        ```bash
        curl -X POST "http://127.0.0.1:8003/nlp/related" -H "Content-Type: application/json" -d '{"text":"손흥민", "vbr_size":1000}'
        ```
    - AWS:
        ```bash
        curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/related" -H "Content-Type: application/json" -d '{"text":"손흥민"}'
        ```

- **성공 응답**:
    ```json
    {
      "code": 200,
      "message": "success",
      "data": [{"keyword":"해외반응","algorithm":0,"score":0.55},{"keyword":"손흥민","algorithm":0,"score":0.45}]
    }
    ```

---

### 📊 비디오 클러스터 API
- **엔드포인트**: `/cluster`
- **메서드**: `POST`
- **설명**: 비디오 정보를 기반으로 클러스터를 분류합니다.
- **요청 바디**:
    ```json
    {
      "title": "KGMA MC 공개!_뉴진스 하니&'굿파트너' 남지현",
      "category": "Entertainment",
      "tags": "['일간스포츠', '연예집합소']",
      "description": "#Hanni #NamJiHyun #Newjeans #goodpartner"
    }
    ```

- **Curl 명령어 예제**:
    - 로컬:
        ```bash
        curl -X POST "http://127.0.0.1:8003/nlp/cluster" -H "Content-Type: application/json" -d '{"title": "KGMA MC 공개!_뉴진스 하니&굿파트너 남지현", "category": "Entertainment", "tags": "[일간스포츠, 연예집합소]", "description": "#Hanni #NamJiHyun #Newjeans"}'
        ```
    - AWS:
        ```bash
        curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/cluster" -H "Content-Type: application/json" -d '{"title": "부산 치과 신경치료 할 때 통증?", "category": "Howto & Style"}'
        ```

- **성공 응답**:
    ```json
    {
      "code": 200,
      "message": "success",
      "data": {
        "cluster_name": "클러스터 이름",
        "cluster_id": 1,
        "cluster_score": 0.95
      }
    }
    ```

---

### 🎥 유사 채널 API
- **엔드포인트**: `/channelsimiler`
- **메서드**: `POST`
- **설명**: 채널 정보를 토대로 유사한 채널을 응답합니다.
- **요청 바디**:
    ```json
    {
      "channel_id":"UC--8ua5dEkuY26fgWkpkz3Q",
      "cluster":14,
      "subscribers":266000,
      "keywords":"코다브릿지, BANANA, LAYSHA",
      "tags":"OMNISOUND",
      "ntop":10
    }
    ```

- **Curl 명령어 예제**:
    - 로컬:
        ```bash
        curl -X POST "http://127.0.0.1:8003/nlp/channelsimiler" -H "Content-Type: application/json" -d '{"channel_id":"UCI3wMpybY12tpc0u33Z-j1w", "cluster":64, "subscribers":266000}'
        ```
    - AWS:
        ```bash
        curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/channelsimiler" -H "Content-Type: application/json" -d '{"channel_id":"UCB116o3mKmmdcdw89rh7Djg"}'
        ```

- **성공 응답**:
    ```json
    {
      "code": 200,
      "message": "success",
      "data": [{"channel_id":"UCB9wEdhMy5Mi8SLNBD-tUrQ","channel_name":"주류학개론"}]
    }
    ```
---

### 🛠️ 문제 해결
- 로그 확인: 문제가 발생하면 `docker logs <container-id>` 명령어로 로그를 확인하여 문제를 해결할 수 있습니다.
