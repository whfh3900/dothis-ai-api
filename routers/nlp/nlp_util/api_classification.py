import os
import sys
sys.path.append("./")
sys.path.append("/app/routers/nlp/nlp_util")
sys.path.append("./routers/nlp/nlp_util")
from dothis_nlp import ZED, PreProcessing, PostProcessing, remove_special_characters, hashtag_extraction
from dotenv import load_dotenv
# .env 파일 경로 지정
dotenv_path = os.path.join(".", '.env')
# .env 파일 로드
load_dotenv(dotenv_path)

class VideoClassification():
    def __init__(self, data_path="./usedata", cache_dir="/home/suchoi/dothis-ai/models/huggingface", use_cuda=True):
        
        self.data_path = data_path
        self.cache_dir = cache_dir
        self.tta_labels = ["artifacts", "person", "animal", "CIVILIZATION", "organization", \
                "phone number", "address", "passport number", "email", "credit card number", \
                "social security number", "health insurance id number", 'Business/organization', \
                "mobile phone number", "bank account number", "medication", "cpf", "driver's license number", \
                "tax identification number", "medical condition", "identity card number", "national id number", \
                "ip address", "email address", "iban", "credit card expiration date", "username", \
                "health insurance number", "student id number", "insurance number", \
                "flight number", "landline phone number", "blood type", "cvv", \
                "digital signature", "social media handle", "license plate number", "cnpj", "postal code", \
                "passport_number", "vehicle registration number", "credit card brand", \
                "fax number", "visa number", "insurance company", "identity document number", \
                "national health insurance number", "cvc", "birth certificate number", "train ticket number", \
                "passport expiration date", "social_security_number", "EVENT", "STUDY_FIELD", "LOCATION", \
                "MATERIAL", "PLANT", "TERM", "THEORY", 'Analysis Requirement']

        self.use_cuda = use_cuda
        self.category_df_path = os.path.join(data_path, "zed_category.csv")
        self.stopwords_path = os.path.join(data_path, "stopwords_for_redis.txt")
        self.josa_path = os.path.join(data_path, "kor_josa.txt")
        self.model_name = "taeminlee/gliner_ko"

        ## 전처리 및 분류 클래스
        self.prep = PreProcessing(model=self.model_name, tta_labels=self.tta_labels, cache_dir=self.cache_dir, 
                                  stopwords_path=self.stopwords_path, use_cuda=self.use_cuda) ## 전처리
        self.posp = PostProcessing(josa_path=self.josa_path, stopwords_path=self.stopwords_path) ## 후처리
        self.zed = ZED(cache_dir=self.cache_dir, category_df=self.category_df_path, use_cuda=self.use_cuda)

    def response(self, title, category, tags, description):
        title = [i[0] for i in self.prep.use_norns(title.strip(), use_upper=True, use_stopword=False, threshold=1.0e-5)]
        tags = [i for i in remove_special_characters(tags).split() if len(i) <= 6]
        hashtags = [i for i in hashtag_extraction(description).split() if len(i) <= 6]
        
        use_text = list()
        use_text.extend(title)
        use_text.extend(tags)
        use_text.extend(hashtags)

        use_text = [i for i in self.posp.post_processing(use_text, use_stopword=True) if i != ""]
        use_text = " ".join(use_text).strip() + " [SEP] " + category
        result = self.zed.classification(use_text)
        return {"use_text":[i.strip() for i in use_text.split('[SEP]')[0].split()],
                "cluster_name":result[0],
                "cluster_id":result[1],
                "cluster_score":result[2]
                }

if __name__ == "__main__":
    title = "크림이 직접 매입,판매를 하고 있단 사실, 알고 계셨나요?(feat. 검수 기준의 무의미함)"
    description = "샵\nhttp://ofad.co.kr/​​​​​​​​​​​\n유튜브 채널\nhttps://www.youtube.com/@OFADTV\n네이버카페\nhttps://cafe.naver.com/ofad\n인스타그램(개인)\nhttps://www.instagram.com/burdock_soo​\n인스타그램(샵)\nhttps://www.instagram.com/ofad_official​\n블로그\nhttps://blog.naver.com/ofad1​​​​​​​​​​​\n페이스북\nhttps://www.facebook.com/ofadofficia\n\n00:00 시작\n01:07 오늘의 사건\n03:25 페이머스 스튜디오의 정체\n05:09 크림 제품은 검수 기준부터 다르다\n07:16 저것들이 끝이 아님"
    tags = "['패션', '오파드', 'fashion', 'ofad', '리셀', 'resell', '크림', 'kream', '크림검수', '크림가품', '가품', '짭', '불량품', '크림짭', '크림정품', '정품', '네이버', '독점', '레플리카', '현미경검수', '검수', '크림법', '소비자보호법', '전자상거래법', '공정위', '소보원', '소비자보호원', '크림소보법', '크림소보자보호법', '크림환불', '공정거래위원회', '독점기업', '독점규제', '실태조사', '플랫폼독점', '독점플랫폼', '갑질', '횡포', '독점갑질', '독점횡포', '크림검수기준', '개인정보', '개인정보법', '개인정보보호법', '나이키매니아', '나매', '페이머스스튜디오', '나이키보디', 'nike', 'bode', 'nikebode', '나이키', '보디', '거래조작', '조작', '주작']"
    category = "Howto & Style"
    
    data_path="./usedata"
    cache_dir="/home/suchoi/dothis-ai/models/huggingface"
    vc = VideoClassification(data_path=data_path,
                      cache_dir=cache_dir)
    
    print(vc.response(title=title, category=category, tags=tags, description=description))