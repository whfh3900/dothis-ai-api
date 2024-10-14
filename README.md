# AI FastAPI 서버

## 시작하기

### 로컬
1. Docker 이미지를 빌드합니다:
```bash
docker build -t ai-fastapi-api-v-c:latest -f dockerfile .
```
2. Docker 컨테이너를 실행합니다:
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

### ECR
1. 개인 브랜치를 만드시고 main 에 PR 주시면 관리자가 ECR + Lambda 배포 진행해주십니다.


## API 사용 방법
### 용언 추출 API
- 엔드포인트: /predicate
- 메서드: POST
- 설명: MeCab을 사용하여 한국어 텍스트를 분석합니다.
- 요청 바디:
```json
{
  "text": "진짜 개재밌다 ㅋㅋㅋ"
}
```
- curl 명령어 예제
#### 로컬
```json
curl -X POST "http://127.0.0.1:8003/nlp/predicate" -H "Content-Type: application/json" -d '{"keyword":"손흥민", "related":"토트넘"}'
```
#### AWS
```json
curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/predicate" -H "Content-Type: application/json" -d '{"keyword":"손흥민", "related":"토트넘"}'
```
#### 응답
- 성공 응답:
```css
{"code":200,"message":"success","data":[{"keyword":"폭발하다","count":126},{"keyword":"밝히다","count":67},{"keyword":"요구하다","count":65},{"keyword":"요청하다","count":64},{"keyword":"반대하다","count":63},{"keyword":"구매하다","count":44},{"keyword":"소개하다","count":44},{"keyword":"불안하다","count":43},{"keyword":"소환되다","count":40},{"keyword":"경악하다","count":28}]}
```
- 에러 응답:
요청 처리 중에 오류가 발생한 경우 적절한 HTTP 상태 코드와 오류 메시지가 반환됩니다.
#### 문제 해결
문제가 발생할 경우 로그 (docker logs <container-id>)를 확인하여 추가 정보를 얻을 수 있습니다.


### 연관어 API
- 엔드포인트: /related
- 메서드: POST
- 설명: 최신데이터 및 Word2vec 알고리즘을 기반으로 연관어를 분석합니다.
- 요청 바디:
```json
{
  "text": "손흥민"
}
```
- curl 명령어 예제
#### 로컬
```json
curl -X POST "http://127.0.0.1:8003/nlp/related" -H "Content-Type: application/json" -d '{"text":"손흥민", "vbr_size":1000}'
```
#### AWS
```json
curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/related" -H "Content-Type: application/json" -d '{"text":"손흥민"}'
```
#### 응답
- 성공 응답:
```css
{
{"code":200,"message":"success","data":[{"keyword":"해외반응","algorithm":0,"score":0.55},{"keyword":"손흥민","algorithm":0,"score":0.45},{"keyword":"축구","algorithm":0,"score":0.4427491928357934},{"keyword":"손흥민골","algorithm":0,"score":0.36371159972676703},{"keyword":"멀티골","algorithm":0,"score":0.3417791693169984},{"keyword":"쏘니","algorithm":0,"score":0.3357265644534358},{"keyword":"맨유스쿼드","algorithm":0,"score":0.33299768029351356},{"keyword":"v11y","algorithm":0,"score":0.3209846390238509},{"keyword":"태극마크","algorithm":0,"score":0.3198948060689162},{"keyword":"멘유","algorithm":0,"score":0.3191606657761809},{"keyword":"에버튼","algorithm":0,"score":0.3179301421027305},{"keyword":"프리미어리그","algorithm":0,"score":0.28752860841971006},{"keyword":"맨유","algorithm":0,"score":0.2863163238491859},{"keyword":"케인","algorithm":0,"score":0.22549162408660975},{"keyword":"김민재","algorithm":0,"score":0.2105399340745465},{"keyword":"일본반응","algorithm":0,"score":0.19375157783122163},{"keyword":"해외축구","algorithm":0,"score":0.19298691018617412},{"keyword":"월드컵","algorithm":0,"score":0.18759285577078227},{"keyword":"인터뷰","algorithm":0,"score":0.18013778573459244}]}
```
- 에러 응답:
요청 처리 중에 오류가 발생한 경우 적절한 HTTP 상태 코드와 오류 메시지가 반환됩니다.
#### 문제 해결
문제가 발생할 경우 로그 (docker logs <container-id>)를 확인하여 추가 정보를 얻을 수 있습니다.


### 비디오 클러스터 API
- 엔드포인트: /cluster
- 메서드: POST
- 설명: 비디오 정보를 기반으로 클러스터를 분류합니다.
- 요청 바디:
```json
{
  "title": "KGMA MC 공개!_뉴진스 하니&'굿파트너' 남지현",
  "category": "Entertainment",
  "tags": "['일간스포츠', '연예집합소', '연예 집합소', '연예', '집합소']",
  "description": "#Hanni #NamJiHyun #Newjeans #goodpartner \n뉴진스 하니와 남지현, 제1회 KGMA 첫날 MC로 출격!\n2024.11.16(SAT) INSPIRE ARENA\n| Authority, Popularity, Globality |\nPlease look forward to the upcoming 2nd lineup✨\n#KGMA #KoreaGrandMusicAwards #뉴진스 #하니\n#코리아그랜드뮤직어워즈 #남지현 #굿파트너\nⓒ Ilgan Sports\nRead us at: https://isplus.com/\nFollow us on Twitter: https://twitter.com/ilgansports"
  }

```
- curl 명령어 예제
#### 로컬
```json
curl -X POST "http://127.0.0.1:8003/nlp/cluster" -H "Content-Type: application/json" -d '{"title": "KGMA MC 공개!_뉴진스 하니&굿파트너 남지현","category": "Entertainment", "tags": "[일간스포츠, 연예집합소, 연예 집합소, 연예, 집합소]","description": "#Hanni #NamJiHyun #Newjeans #goodpartner"}'
```
#### AWS
```json
curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/cluster" -H "Content-Type: application/json" -d '{"title": "부산 치과 신경치료 할 때 통증?","category": "Howto & Style","tags": "['부산신경치료', '신경치료통증', '치아신경치료']","description": "이 동영상 의료상담 답변은 '환자와 의사를 잇는' 닥톡에서 배포합니다.\n출처 : https://www.doctalk.co.kr/counsel/view/c-4tZV7FKD-cR8u-4i16-ctxC-6EHjRvG9LXEP\n치과 신경치료할때 얼마나 아프나요?\n많이 아프다고 들어서요"}'
```
#### 응답
- 성공 응답:
```css
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
- 에러 응답:
요청 처리 중에 오류가 발생한 경우 적절한 HTTP 상태 코드와 오류 메시지가 반환됩니다.
#### 문제 해결
문제가 발생할 경우 로그 (docker logs <container-id>)를 확인하여 추가 정보를 얻을 수 있습니다.



### 유사 채널 API
- 엔드포인트: /channelsimiler
- 메서드: POST
- 설명: 채널정보를 토대로 유사한 채널을 응답합니다.
- 요청 바디:
```json
{
    "channel_id":"UC--8ua5dEkuY26fgWkpkz3Q",
    "cluster":14,
    "subscribers":266000,
    "keywords":"코다브릿지, BANANA, LAYSHA, 반하나, 시진",
    "tags":"OMNISOUND, 물빛무대, 여의도한강공원",
    "ntop":10,
  }

```
- curl 명령어 예제
#### 로컬
```json
curl -X POST "http://127.0.0.1:8003/nlp/channelsimiler" -H "Content-Type: application/json" -d '{"channel_id":"UCI3wMpybY12tpc0u33Z-j1w", "cluster":64, "subscribers":266000, "keywords":"싱글몰트, 면세점, 위스키칵테일, 스카치, 바텐더", "tags":"위스키, 칵테일, 하이볼, 비교시음", "ntop":10}'
```
#### AWS
```json
curl -X POST "https://g6g5ootucv57t73ghafllwpbv40ghclt.lambda-url.ap-northeast-2.on.aws/nlp/channelsimiler" -H "Content-Type: application/json" -d '{"channel_id":"UCB116o3mKmmdcdw89rh7Djg", "cluster":64, "subscribers":266000, "keywords":"UPLOAD, 위스키추천, 끝장토론, 위스키리뷰, 위린이", "tags":"위스키, 위스키추천, 위스키리뷰, 위린이, WHISKY", "ntop":10}'
```
#### 응답
- 성공 응답:
```css
{"code":200,"message":"success","data":[{"channel_id":"UCB9wEdhMy5Mi8SLNBD-tUrQ","channel_name":"주류학개론 - 재미있는 술의 비하인드 스토리","mainly_used_keywords":"바텐더, 바텐딩, 주류학, 주류학개론, 싱글몰트","mainly_used_tags":"위스키, 주류학개론, 싱글몰트, 버번위스키, 스카치위스키","channel_thumbnail":"https://yt3.googleusercontent.com/ytc/AIdro_kRtOaK4GcsqIScFtnH9uCsSbro1-7txGR9C-MgR6wg0g=s900-c-k-c0x00ffffff-no-rj","channel_average_views":61908.0,"channel_subscribers":359000,"channel_total_videos":500,"score":0.1805039942264557},{"channel_id":"UCzcfJg60HoTrZ0MwsA5PpIA","channel_name":"푸딩 / Pudding","mainly_used_keywords":"고민상담, 개그콘서트, 복현규, 포도주, 건강관리","mainly_used_tags":"고민상담, 원샷원킬, 고민타파, 와인리뷰, 와인","channel_thumbnail":"https://yt3.googleusercontent.com/stuIp3uyhVceTb_H5o-CRGvGdm_6C2vckduzdDVMGg-iJKbSdHi4IwrpxtzIs5wShWv1t_IC=s900-c-k-c0x00ffffff-no-rj","channel_average_views":2490.0,"channel_subscribers":236000,"channel_total_videos":198,"score":0.1674298346042633},{"channel_id":"UC1FZ59NCoUOpveg6nP6Dm-A","channel_name":"어쿠스틱 드링크","mainly_used_keywords":"위스키","mainly_used_tags":"위스키, 칵테일","channel_thumbnail":"https://yt3.googleusercontent.com/5QgvM0UELef1nCRnB5FP6BojeU-QtbAa0HSHXqQbAFZJI4T2yAhoC7g3DNhEUiSLGDFEubbWeaI=s900-c-k-c0x00ffffff-no-rj","channel_average_views":0.0,"channel_subscribers":426000,"channel_total_videos":327,"score":0.12848323583602905},{"channel_id":"UCzKFT7cBIKO9Dapikf6e3ow","channel_name":"롯데칠성 LOTTE CHILSUNG","mainly_used_keywords":"김우빈, 모델, 오피스커피, 특별한휴식, 휴식","mainly_used_tags":"BETTERNEXTFROMCANTATA, 김우빈, 모델, 더나은다음을향해, 직장인필수템","channel_thumbnail":"https://yt3.googleusercontent.com/ahQh1iC7spbbQlwtJqW1ISh9q6mpcDMu1XBbee0bZi_3T3clScstb_RFnfs_mY8R6DYElljder8=s900-c-k-c0x00ffffff-no-rj","channel_average_views":327595.0,"channel_subscribers":115000,"channel_total_videos":438,"score":0.1274861842393875},{"channel_id":"UCip7tR0D_33uoQTh0tVxeEQ","channel_name":"얀콘 Yancon","mainly_used_keywords":"하이볼","mainly_used_tags":"","channel_thumbnail":"https://yt3.googleusercontent.com/ytc/AIdro_mB2o47Q6A80vwrEBHxUtizrwMpVtHynga4VVWWo2USeIk=s900-c-k-c0x00ffffff-no-rj","channel_average_views":27607.0,"channel_subscribers":128000,"channel_total_videos":224,"score":0.10688343644142151},{"channel_id":"UCOPU_dB2wxkZEW2ym7PAixw","channel_name":"Taylor 909","mainly_used_keywords":"젤로","mainly_used_tags":"마르키사","channel_thumbnail":"https://yt3.googleusercontent.com/ytc/AIdro_kBRr9gMIrviyk7GkYvV4tEyvVhONuoIe38fxXVP9Frt64=s900-c-k-c0x00ffffff-no-rj","channel_average_views":50998.0,"channel_subscribers":154000,"channel_total_videos":93,"score":0.06730415672063828},{"channel_id":"UCGtY9qyrQqqPlkNqAwccjNQ","channel_name":"리뷰하는 회사원","mainly_used_keywords":"브이로그, 숙취해소제, 선물, 추석, 맛집","mainly_used_tags":"숙취해소제, 리뷰하는회사원","channel_thumbnail":"https://yt3.googleusercontent.com/2yhcmSINfstpsVqZqyXxwbQG1VCXh5mVN2mcPHo2zKfSjYGCfFQ4WZk18ShttEQci6w1gv16m_0=s900-c-k-c0x00ffffff-no-rj","channel_average_views":60692.0,"channel_subscribers":433000,"channel_total_videos":713,"score":0.045273296535015106},{"channel_id":"UCzuVLt12gtYVshSV7s-JfZQ","channel_name":"춤추는선진이","mainly_used_keywords":"향수리뷰, 살냄새, 니치향수, 향수소개, 딥티크","mainly_used_tags":"향수추천, 록시땅, 니치향수","channel_thumbnail":null,"channel_average_views":25798.0,"channel_subscribers":139000,"channel_total_videos":462,"score":0.016982052475214005},{"channel_id":"UC5XiIXSEQwk9Pq-Drnq8zQA","channel_name":"생명의물-위스키를 즐겁게","mainly_used_keywords":"whisky, 메막, 을지로, 야마자키, 메이커스","mainly_used_tags":"whisky, 메막, 을지로, 야마자키, 메이커스","channel_thumbnail":"https://yt3.googleusercontent.com/ytc/AIdro_lge2Vd7c0LD2dY2R3VsuI8rRQl2Dnlm0Ut7RH76P4JBw=s900-c-k-c0x00ffffff-no-rj","channel_average_views":25882.0,"channel_subscribers":224000,"channel_total_videos":1875,"score":0.016636649146676064}]}

```
- 에러 응답:
요청 처리 중에 오류가 발생한 경우 적절한 HTTP 상태 코드와 오류 메시지가 반환됩니다.
#### 문제 해결
문제가 발생할 경우 로그 (docker logs <container-id>)를 확인하여 추가 정보를 얻을 수 있습니다.