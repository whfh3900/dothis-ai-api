import os
import json
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
from redis.sentinel import Sentinel
from util.log_function import logger
# .env 파일 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
# .env 파일 로드
load_dotenv(dotenv_path)


# 환경 변수에서 값 가져오기
hash_key = os.getenv('HASH_KEY').encode()
redis_sentinel_password = os.getenv('REDIS_SENTINEL_PASSWORD')
redis_sentinel_node1 = os.getenv('REDIS_SENTINEL_NODE1')
redis_sentinel_node2 = os.getenv('REDIS_SENTINEL_NODE2')
redis_sentinel_node3 = os.getenv('REDIS_SENTINEL_NODE3')

# Fernet 객체 생성
cipher = Fernet(hash_key)

# Redis Sentinel 설정
sentinel_hosts = [
    (cipher.decrypt(redis_sentinel_node1).decode(), 3400),
    (cipher.decrypt(redis_sentinel_node2).decode(), 3400),
    (cipher.decrypt(redis_sentinel_node3).decode(), 3400)
]

# Redis Sentinel 연결
try:
    sentinel = Sentinel(sentinel_hosts, socket_timeout=0.1)
    master = sentinel.master_for('redismaster', socket_timeout=0.1, password=cipher.decrypt(redis_sentinel_password).decode())
except Exception as e:
    logger.error(f"Redis Sentinel connection failed: {e}")
    exit(1)

# 정보 업데이트 및 저장 함수
def save_info(endpoint_alias, data):
    # 데이터를 JSON으로 변환하고 암호화
    key = f"info:{endpoint_alias}"
    current_data = {}
    
    try:
        # 현재 저장된 데이터 가져오기
        encrypted_data = master.get(key)
        if encrypted_data:
            current_data = json.loads(cipher.decrypt(encrypted_data).decode())
        
        # 새로운 데이터 업데이트
        updated_data = {**current_data, **data}  # 기존 데이터와 새 데이터 병합
        
        # 암호화하여 Redis에 저장
        encrypted_data = cipher.encrypt(json.dumps(updated_data).encode())
        master.set(key, encrypted_data.decode())
        
        # .env 파일에 백업
        backup_to_env(endpoint_alias, current_data, data)  # 변경된 데이터와 새 데이터 전달
        
        logger.info(f"Data saved for {key}: {updated_data}")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def backup_to_env(endpoint_alias, existing_data, new_data):
    # .env 파일에서 기존 데이터 가져오기
    env_key = f"{endpoint_alias.upper()}_INFO"
    existing_data_json = os.getenv(env_key)
    
    # 기존 데이터가 있으면 업데이트, 없으면 새로 추가
    if existing_data_json:
        existing_data_dict = json.loads(existing_data_json)
        existing_data_dict.update(new_data)  # 새 데이터만 업데이트
        # 업데이트된 데이터를 .env에 저장
        set_key(dotenv_path, env_key, json.dumps(existing_data_dict))
    else:
        # 새 데이터 추가
        set_key(dotenv_path, env_key, json.dumps(new_data))

# 정보 가져오기 함수
def get_info(endpoint_alias):
    key = f"info:{endpoint_alias}"
    try:
        encrypted_data = master.get(key)
        if encrypted_data:
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        else:
            logger.info(f"No data found for {key}.")
            return None
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        return None