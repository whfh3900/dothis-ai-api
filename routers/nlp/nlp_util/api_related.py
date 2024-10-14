import os
import sys
sys.path.append("/app/routers/nlp/util")
sys.path.append("./routers/nlp/util")
from dothis_keyword import VBR, GensimRelated
from ai_dataload import download_file_from_s3
import math
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
    

class Related():
    def __init__(self, bucket_name="dothis-ai", 
                 s3_prefix="models/related/",
                 local_dir=f"/home/suchoi/dothis-ai/models/related/",
                 data_path = "./usedata"):

        self.bucket_name = bucket_name
        self.s3_prefix = s3_prefix
        self.local_dir = local_dir
        self.data_path = data_path

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)

        download_file_from_s3(bucket_name=self.bucket_name,
                            s3_prefix=self.s3_prefix,
                            local_dir=self.local_dir)

        self.gr_path = os.path.join(self.local_dir, "related_model.bin")
        self.josa_path = os.path.join(self.data_path, "kor_josa.txt")
        self.stopwords_path = os.path.join(self.data_path, "stopwords_for_related.txt")
        self.model = "word2vec"

        self.gr = GensimRelated(path=self.gr_path,
                        josa_path=self.josa_path,
                        stopwords_path=self.stopwords_path,
                        model=self.model)

        # self.df = vbr_data_collect()
        self.vbr = VBR(josa_path=self.josa_path, stopwords_path=self.stopwords_path)

    def response(self, word, vbr_threadholds=5, vbr_size=1000, vbr_ntop=10, inference_ntop=10, vbr_ratio=0.55, inference_ratio=0.45):
        ntop = vbr_ntop+inference_ntop
        related_inference = self.gr.gensim_related(word, ntop=None, split_word_check=True)
        vbr_related = self.vbr.related(word, threadholds=vbr_threadholds, size=vbr_size, ntop=None)

        classificate = -1
        combined_dict = dict()
        
        if (len(related_inference) > 0) and (len(vbr_related) > 0):
            classificate = 0
            vbr_score_scales = [(x / max(vbr_related.values())) * vbr_ratio for x in vbr_related.values()]
            inference_score_scales = [(x / max(related_inference.values())) * inference_ratio for x in related_inference.values()]
            # 업데이트
            vbr_related = dict(zip(vbr_related.keys(), vbr_score_scales))
            related_inference = dict(zip(related_inference.keys(), inference_score_scales))
            # 두 딕셔너리의 모든 연관어 모음
            all_related_word = list(set(vbr_related.keys()) | set(related_inference.keys()))
            
            ### dict.get(key, default)로 해당 연관어가 없으면 0이 반환되도록 함.
            for related_word in all_related_word:
                vbr_score_value = vbr_related.get(related_word, 0)
                inference_score_value = related_inference.get(related_word, 0)
                
                combined_score = vbr_score_value + inference_score_value
                ### combined_score가 null값이거나 0이 아닌 경우에만 저장
                if (not math.isnan(combined_score)) and (combined_score != 0):
                    combined_dict[related_word] = combined_score
            # 값을 기준으로 내림차순 정렬
            combined_dict = dict(sorted(combined_dict.items(), key=lambda item: item[1], reverse=True))
        
        elif (len(related_inference) > 0) and (len(vbr_related) == 0):          
            classificate = 1          
            inference_score_scales = [(x / max(related_inference.values())) * inference_ratio for x in related_inference.values()]
            related_inference = dict(zip(related_inference.keys(), inference_score_scales))
            # 값을 기준으로 내림차순 정렬
            combined_dict = dict(sorted(related_inference.items(), key=lambda item: item[1], reverse=True))
            
        elif (len(related_inference) == 0) and (len(vbr_related) > 0):       
            classificate = 2             
            vbr_score_scales = [(x / max(vbr_related.values())) * vbr_ratio for x in vbr_related.values()]
            vbr_related = dict(zip(vbr_related.keys(), vbr_score_scales))
            # 값을 기준으로 내림차순 정렬
            combined_dict = dict(sorted(vbr_related.items(), key=lambda item: item[1], reverse=True))

        if len(combined_dict) > 0:
            combined_dict = dict(list(combined_dict.items())[:ntop])
            return [{"keyword":key, 
                    "algorithm":classificate, 
                    "score":value} for key, value in combined_dict.items()]
        else:
            return 


if __name__ == "__main__":
    bucket_name="dothis-ai"
    s3_prefix="models/related"
    local_dir=f"/home/suchoi/dothis-ai/models/related"
    data_path = "./usedata"
    r = Related(bucket_name=bucket_name, s3_prefix=s3_prefix,
            local_dir=local_dir, data_path=data_path)
    word = "파리올림픽"
    print(r.response(word, vbr_ratio=0.55, inference_ratio=0.45))