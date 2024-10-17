import asyncio
import re
import os
from util.log_function import logger
from util.redis_keyvault import get_info
import sys
sys.path.append("/app/routers/nlp/nlp_util")
sys.path.append("./routers/nlp/nlp_util")
import traceback
from fastapi.responses import JSONResponse
from dothis_keyword import Verb
env = get_info("dothis-fastapi-ai")
path = env.get('LAMBDA_TASK_ROOT')
from dotenv import load_dotenv
# .env 파일 경로 지정
dotenv_path = os.path.join(".", '.env')
# .env 파일 로드
load_dotenv(dotenv_path)

if path is None:
    path = "/app"

mecab_dic_path = f"{path}/mecab-ko-dic-2.1.1-20180720"
data_path = "/app/usedata"
stopwords_path = os.path.join(data_path, "stopwords_for_verb.txt")

predicate = Verb(stopwords_path=stopwords_path, mecab_dic_path=f"{path}/mecab-ko-dic-2.1.1-20180720")

async def main(body: dict):
    try:
        keyword = body["keyword"]
        related = body["related"]
        
        # result = await predicate.predict(keyword, related, days=31, size=20000, top=10)
        result = predicate.predict(keyword, related, days=31, size=20000, top=10)

        response_data = [{"keyword":key,
                            "count":value} for key, value in result.items()]
        if len(response_data) == 0:
            logger.error(traceback.format_exc())
            logger.error(body)
            return {
                "code": 404,
                "message": f"faild: No relationship found between keyword and related word {keyword}, {related}"
                }
        
        return JSONResponse({"code":200,
                                "message":"success",
                                "data":response_data})
    except KeyError:
        logger.error(traceback.format_exc())
        logger.error(body)
        return {
            "code": 400,
            "message": f"faild: Request body should contain 'keyword' or 'related' field"
            }
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(body)
        return {
            "code": 500,
            "message": str(e)
            }
