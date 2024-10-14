import pymysql
import os
import sys
sys.path.append("/app/routers/nlp/util")
sys.path.append("./routers/nlp/util")
from datetime import datetime, timedelta
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
import numpy as np

try:
    from util.log_function import logger
    from util.redis_keyvault import get_info
    env = get_info("dothis-fastapi-ai")
    path = env.get('LAMBDA_TASK_ROOT')

except ModuleNotFoundError:
    from dotenv import load_dotenv
    # .env 파일 경로 지정
    dotenv_path = os.path.join(".", '.env')
    # .env 파일 로드
    load_dotenv(dotenv_path)
    path = None
    
class ChannelSimilar():
    def __init__(self):
        try:
            host = env.get('MYSQL_HOST') # RDS 엔드포인트 URL 또는 IP 주소
            port = int(env.get('MYSQL_PORT')) # RDS 데이터베이스 포트 (기본값: 3306)
            user = env.get('MYSQL_USER') # MySQL 계정 아이디
            password = env.get('MYSQL_PW') # MySQL 계정 비밀번호
        except Exception as e:
            print(e)
            host = os.environ.get('MYSQL_HOST') # RDS 엔드포인트 URL 또는 IP 주소
            port = int(os.environ.get('MYSQL_PORT')) # RDS 데이터베이스 포트 (기본값: 3306)
            user = os.environ.get('MYSQL_USER') # MySQL 계정 아이디
            password = os.environ.get('MYSQL_PW') # MySQL 계정 비밀번호
        
        self.db_name = "dothis_svc"
        # PROXMOX MySQL 연결하기
        self.conn = pymysql.connect(host=host, 
                                port=port, 
                                user=user, 
                                password=password, 
                                db=self.db_name, 
                                charset='utf8mb4')

        # 데이터베이스 커서(Cursor) 객체 생성
        self.cursor = self.conn.cursor()
        
        self.yearmonth = datetime.today().strftime("%Y%m")
        query = f"desc channel_data;"
        self.cursor.execute(query)
        columns = [i[0] for i in self.cursor.fetchall()]
        columns.extend(["channel_subscribers", "channel_average_views", "channel_total_videos"])

        query = f"""
                WITH latest_history AS (
                    SELECT channel_id, channel_subscribers, channel_average_views, channel_total_videos
                    FROM channel_history_{self.yearmonth} AS ch
                    WHERE day = (
                        SELECT MAX(day)
                        FROM channel_history_{self.yearmonth} AS ch2
                        WHERE ch.channel_id = ch2.channel_id
                    )
                )
                SELECT cd.*, lh.channel_subscribers, lh.channel_average_views, lh.channel_total_videos
                FROM channel_data cd
                JOIN latest_history lh ON cd.channel_id = lh.channel_id;
                """
        self.cursor.execute(query)
        self.df = pd.DataFrame(self.cursor.fetchall(), columns=columns)
        self.df["subscribers_cluster"] = self.df["channel_subscribers"].apply(lambda x: self.subscribers_range(x))
        
    # 구독자 범위 클러스터
    def subscribers_range(self, subscribers):
        if subscribers < 1000:
            return 0
        elif subscribers >= 1000 and subscribers < 10000:
            return 1
        elif subscribers >= 10000 and subscribers < 50000:
            return 2
        elif subscribers >= 50000 and subscribers < 100000:
            return 3
        elif subscribers >= 100000 and subscribers < 500000:
            return 4
        elif subscribers >= 500000 and subscribers < 1000000:
            return 5
        elif subscribers >= 1000000 and subscribers < 5000000:
            return 6
        elif subscribers >= 5000000 and subscribers < 10000000:
            return 7
        else:
            return 8

    def scale_scores(self, dict_list, new_min=0.1, new_max=0.9):
        scores = [d['score'] for d in dict_list]
        min_score = min(scores)
        max_score = max(scores)
        
        for d in dict_list:
            scaled_value = ((d['score'] - min_score) / (max_score - min_score)) * (new_max - new_min) + new_min
            # 클리핑 작업으로 값이 new_min과 new_max 사이에 있도록 제한
            d['score'] = max(min(scaled_value, new_max), new_min)
        
        return dict_list
    
    def get_sentence_vector(self, sentence, model):
        vectors = [model.wv[word] for word in sentence if word in model.wv]
        return np.mean(vectors, axis=0)

    def response(self, channel_id, cluster, subscribers, keywords, tags, ntop=10):
        
        keywords = [i.strip() for i in keywords.split(",")]
        tags = [i.strip() for i in tags.split(",") if i.strip()]  # 공백만 있는 항목 제거
        if tags:  # 빈 리스트가 아닌 경우에만 실행
            keywords.extend(tags)
        
        subscribers_cluster = self.subscribers_range(subscribers)
        results = self.df[(self.df.CHANNEL_CLUSTER == cluster) & 
                    (self.df.subscribers_cluster.isin([subscribers_cluster+1, subscribers_cluster, subscribers_cluster-1])) & 
                    (self.df.MAINLY_USED_KEYWORDS != "")].copy()
        results["target_keywords"] = results.apply(lambda x: [i.strip() for i in x.MAINLY_USED_KEYWORDS.split(",")] + [i.strip() for i in x.MAINLY_USED_TAGS.split(",")], axis=1)
        results.reset_index(drop=True, inplace=True)
        ### 1) 포함 여부만으로 값 찾기
        response_data = list()
        first_results = results[results.target_keywords.apply(lambda x: any(keyword in x for keyword in keywords))]
        first_results = first_results[(first_results.CHANNEL_ID != channel_id)]
        if len(first_results) > 0:
            # 스코어 컬럼 추가
            first_results = first_results.copy()
            first_results['score'] = first_results['target_keywords'].apply(lambda x: 1+(len(set(keywords) & set(x))) / (len(set(keywords) | set(x))))
            
            for row in first_results.iterrows():
                data = dict()
                data["channel_id"] = row[1].CHANNEL_ID
                data["channel_name"] = row[1].CHANNEL_NAME
                data["mainly_used_keywords"] = row[1].MAINLY_USED_KEYWORDS
                data["mainly_used_tags"] = row[1].MAINLY_USED_TAGS
                data["channel_thumbnail"] = row[1].CHANNEL_THUMBNAIL
                data["channel_average_views"] = row[1].channel_average_views
                data["channel_subscribers"] = row[1].channel_subscribers
                data["channel_total_videos"] = row[1].channel_total_videos
                data["score"] = row[1].score
                data["classificate"] = 1
                response_data.append(data)
            
            response_data = sorted(response_data, key=lambda x: x['score'], reverse=True)
            ntop = ntop-len(first_results)
        if ntop < 1:
            response_data = self.scale_scores(response_data)[:ntop]
            return response_data
        
        ### 2) word2vec 기반의 임베딩으로 값 찾기
        word2vec_data = results["target_keywords"].tolist()
        word2vec_data.append(keywords)
        
        model = Word2Vec(word2vec_data, vector_size=500, window=5, min_count=1, workers=18, epochs=50)
        second_results = results[(results.CHANNEL_ID != channel_id)]
        second_results = second_results[~second_results.CHANNEL_ID.isin(first_results.CHANNEL_ID.tolist())].copy()
        second_results.reset_index(drop=True, inplace=True)

        vector1 = self.get_sentence_vector(keywords, model).reshape(1, -1)
        word2vec_result = dict()
        for row in second_results.iterrows():
            target_cid = row[1].CHANNEL_ID
            if target_cid != channel_id:
                vector2 = self.get_sentence_vector(row[1].target_keywords, model).reshape(1, -1)
                # 코사인 유사도 계산
                cos_sim = cosine_similarity(vector1, vector2)[0][0]
                if cos_sim > 0:
                    word2vec_result[target_cid] = cos_sim

        word2vec_result = dict(sorted(word2vec_result.items(), key=lambda item: item[1], reverse=True))
        second_results = second_results[second_results.CHANNEL_ID.isin(word2vec_result.keys())].copy()
        second_results['score'] = word2vec_result.values() - .2
        second_results.reset_index(drop=True, inplace=True)
        
        for row in second_results.iterrows():
            data = dict()
            data["channel_id"] = row[1].CHANNEL_ID
            data["channel_name"] = row[1].CHANNEL_NAME
            data["mainly_used_keywords"] = row[1].MAINLY_USED_KEYWORDS
            data["mainly_used_tags"] = row[1].MAINLY_USED_TAGS
            data["channel_thumbnail"] = row[1].CHANNEL_THUMBNAIL
            data["channel_average_views"] = row[1].channel_average_views
            data["channel_subscribers"] = row[1].channel_subscribers
            data["channel_total_videos"] = row[1].channel_total_videos
            data["score"] = row[1].score
            data["classificate"] = 2
            response_data.append(data)
        
        response_data = self.scale_scores(response_data)
        response_data = sorted(response_data, key=lambda x: x['score'], reverse=True)[:ntop]
        return response_data
    
if __name__ == "__main__":
    import pprint

    cs = ChannelSimilar()
    channel_id = "UCGt0EaD1_eCmASkew4MrFTg"
    cluster = 0
    # cluster = 45
    subscribers = 1440
    # keywords = "D8WS, 엔진버기, 핫바디, GDRC, 주행, D819RS, E8WS, RC카, 키덜트, 진천서킷"
    keywords = "피프티피프티"
    tags = ""
    # tags = "핫바디, GDRC, 엔진버기, 키덜트, E8WS, 주행, D819RS, 진천서킷, 랠리카, MJX"
    ntop = 10
    result = cs.response(channel_id=channel_id, cluster=cluster, subscribers=subscribers, keywords=keywords, tags=tags)
    for i in result:
        pprint.pprint(i)
