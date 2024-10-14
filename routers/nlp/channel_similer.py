import os
from fastapi.responses import JSONResponse
import sys
sys.path.append("/app/routers/nlp/nlp_util")
sys.path.append("./routers/nlp/nlp_util")
from api_channel_similar import ChannelSimilar
import traceback

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
    

if path is None:
    path = "/app"

cs = ChannelSimilar()


async def main(body: dict):
    try:
        # 기본값을 10으로 설정
        ntop = int(body.get("ntop", 10))
        channel_id = body["channel_id"]
        cluster = int(body["cluster"])
        subscribers = int(body["subscribers"])
        keywords = body["keywords"]
        tags = body["tags"]
        if (keywords=="") & (tags==""):
            logger.error(traceback.format_exc())
            logger.error(body)
            return {
                "code": 400,
                "message": f"faild: Request body should contain 'keywords' and 'tags' field"
                }
        
        response_data = cs.response(channel_id=channel_id, 
                                    cluster=cluster, 
                                    subscribers=subscribers, 
                                    keywords=keywords, tags=tags,
                                    ntop=ntop)

        if len(response_data) != 0:
            return JSONResponse({"code":200,
                                 "message":"success",
                                 "data":response_data})
        else:
            return {
                "code": 404,
                "message": f"faild: No associated words found for that word '{word}'"
            }
    except KeyError:
        logger.error(traceback.format_exc())
        logger.error(body)
        return {
            "code": 400,
            "message": f"faild: Request body should contain 'text' field"
            }
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(body)
        return {
            "code": 500,
            "message": str(e)
            }
