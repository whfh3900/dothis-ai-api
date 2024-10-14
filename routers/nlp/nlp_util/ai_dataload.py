import os
import pandas as pd
from datetime import datetime, timedelta
import pymysql
import boto3
import sys
import traceback
from opensearchpy import OpenSearch
from dothis_nlp import decode_and_convert

try:
    from util.log_function import logger
    from util.redis_keyvault import get_info
    env = get_info("dothis-fastapi-ai")
except ModuleNotFoundError:
    from dotenv import load_dotenv
    # .env 파일 경로 지정
    dotenv_path = os.path.join(".", '.env')
    # .env 파일 로드
    load_dotenv(dotenv_path)



def download_file_from_s3(bucket_name, s3_prefix, local_dir):
    """
    S3에서 파일을 다운로드하여 로컬 디렉토리에 저장합니다.
    
    :param bucket_name: S3 버킷 이름
    :param s3_prefix: S3에서 폴더의 경로 (예: 'path/to/folder/')
    :param local_dir: 로컬 디렉토리 경로
    """
    try:
        # 환경 변수에서 AWS 자격 증명 읽기
        aws_access_key_id = env.get('AWS_IAM_ACCESS_KEY')
        aws_secret_access_key = env.get('AWS_IAM_SECRET_KEY')
    except NameError:
        # 환경 변수에서 AWS 자격 증명 읽기
        aws_access_key_id = os.environ.get('AWS_IAM_ACCESS_KEY')
        aws_secret_access_key = os.environ.get('AWS_IAM_SECRET_KEY')
    aws_region = 'ap-northeast-2'  # 한국 리전
    
    # AWS 자격 증명을 사용하여 S3 클라이언트 생성
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    
    # 로컬 디렉토리 확인 및 생성
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # S3 객체 목록 가져오기
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
    
    if 'Contents' not in response:
        print("No files found in the specified S3 folder.")
        logger.info("No files found in the specified S3 folder.")
        return
    
    for obj in response['Contents']:
        # 파일 경로 및 이름 추출
        s3_key = obj['Key']
        filename = os.path.basename(s3_key)
        
        # 파일의 로컬 디렉토리 경로가 아닌 파일 경로 확인
        local_file_path = os.path.join(local_dir, filename)
        
        # 파일이 아니라 디렉토리인 경우 처리
        if os.path.isdir(local_file_path):
            print(f"Skipping directory {local_file_path}")
            logger.info(f"Skipping directory {local_file_path}")
            continue
        
        # S3에서 파일 다운로드
        print(f"Downloading {s3_key} to {local_file_path}")
        logger.info(f"Downloading {s3_key} to {local_file_path}")
        s3.download_file(bucket_name, s3_key, local_file_path)
        print(f"Downloaded {s3_key} to {local_file_path}")
        logger.info(f"Downloaded {s3_key} to {local_file_path}")



def vbr_data_collect():
    try:
        host = env.get('OPENSEARCH_HOST') # RDS 엔드포인트 URL 또는 IP 주소
        port = int(env.get('OPENSEARCH_PORT')) # RDS 데이터베이스 포트 (기본값: 3306)
        user = env.get('OPENSEARCH_USER') # MySQL 계정 아이디
        password = env.get('OPENSEARCH_PW') # MySQL 계정 비밀번호
    except Exception as e:
        print(e)
        host = os.environ.get('OPENSEARCH_HOST') # RDS 엔드포인트 URL 또는 IP 주소
        port = int(os.environ.get('OPENSEARCH_PORT')) # RDS 데이터베이스 포트 (기본값: 3306)
        user = os.environ.get('OPENSEARCH_USER') # MySQL 계정 아이디
        password = os.environ.get('OPENSEARCH_PW') # MySQL 계정 비밀번호

    # OpenSearch 클러스터에 연결
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(user, password),
        use_ssl=True,
        verify_certs=False,  # SSL 인증서 검증 비활성화
        time_out=360
    )
    try:
        health = client.cluster.health()
        print("Cluster health:", health)
    except Exception as e:
        print("Error connecting to OpenSearch:", e)
    

    size = 100000
    end_date = datetime.now()
    end_date_str = end_date.strftime("%Y-%m-%d")
    start_date = end_date - timedelta(days=7, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    start_date_str = start_date.strftime("%Y-%m-%d")
    columns = ["@timestamp", "video_views", "video_id", "use_text"]
    
    try:
        logger.info(f"OpenSearch scrolls data for VBR.")
    except NameError:
        pass
    
    print("OpenSearch scrolls data for VBR.")    
    scroll_duration = '2m'
    query = {
        "size": size,  # 최대 100000개의 결과 반환
        "_source": columns,  # 반환할 필드 지정
        "query": {
            "bool": {
            "filter": [
                {
                "range": {
                    "@timestamp": {
                        "gte": start_date_str,  # 시작 날짜 (포함)
                        "lte": end_date_str   # 종료 날짜 (포함)
                    }
                }
                }
            ]
            }
        }
    }

    # 초기 검색 요청 및 스크롤 시작
    response = client.search(
        index="video_history",
        body=query,
        scroll=scroll_duration  # 스크롤 유지 시간 설정
    )

    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']

    # 검색된 문서를 데이터프레임에 저장
    df = pd.DataFrame([hit['_source'] for hit in hits])

    while True:
        # 스크롤 요청을 사용하여 다음 데이터 셋 가져오기
        response = client.scroll(
            scroll_id=scroll_id,
            scroll=scroll_duration  # 스크롤 유지 시간 설정
        )

        hits = response['hits']['hits']

        # 더 이상 결과가 없으면 루프 종료
        if not hits:
            break

        # 검색된 문서를 데이터프레임에 추가
        etc = pd.DataFrame([hit['_source'] for hit in hits])
        df = pd.concat([df, etc], axis=0)

        # 스크롤 ID 갱신
        scroll_id = response['_scroll_id']

    # 1. @timestamp 열을 datetime 형식으로 변환
    df['@timestamp'] = pd.to_datetime(df['@timestamp'], errors='coerce')  # 오류 발생 시 NaT로 설정
    for col in columns:
        # 2. 결측값(NaN) 제거
        df = df.dropna(subset=[col])
        
    df['use_text'] = df['use_text'].apply(lambda x: " ".join(x))
    # 데이터프레임 인덱스 재설정
    df.reset_index(drop=True, inplace=True)

    try:
        logger.info(f"Start video_views calculation")
    except NameError:
        pass
    print("Start video_views calculation")
    recent_views = df.loc[df.groupby('video_id')['@timestamp'].idxmax(), ['video_id', 'video_views']].rename(columns={'video_views': 'video_views_recent'})
    oldest_views = df.loc[df.groupby('video_id')['@timestamp'].idxmin(), ['video_id', 'video_views']].rename(columns={'video_views': 'video_views_oldest'})

    # 최근 날짜와 오래된 날짜의 video_views의 차이 계산
    views_diff = recent_views.merge(oldest_views, on='video_id', suffixes=('_recent', '_oldest'))
    views_diff.columns = ["video_id", "video_views_recent", "video_views_oldest"]
    views_diff['weekly_views'] = views_diff['video_views_recent'] - views_diff['video_views_oldest']

    # weekly_views가 0인 경우, video_views_recent 값으로 변경
    views_diff['weekly_views'] = np.where(views_diff['weekly_views'] == 0, views_diff['video_views_recent'], views_diff['weekly_views'])
    views_diff.drop(['video_views_recent', 'video_views_oldest'], axis=1, inplace=True)
    
    try:
        logger.info(f"Dataset ready for VBR")
    except NameError:
        pass
    print("Dataset ready for VBR")
    return views_diff


if __name__ == "__main__":
    path = "testdata/vbr.csv"
    df = vbr_data_collect()
    df.to_csv(path, encoding="utf-8-sig")
