import os
from fastapi.responses import JSONResponse
import sys
sys.path.append("/app/routers/nlp/nlp_util")
sys.path.append("./routers/nlp/nlp_util")
from api_related import Related
import math
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

s3_prefix="models/related/"
local_dir = f"/app/{s3_prefix}"
data_path = "/app/usedata"
bucket_name="dothis-ai"

r = Related(local_dir=local_dir,
            data_path=data_path,
            bucket_name=bucket_name,
            s3_prefix=s3_prefix)

async def main(body: dict):
    try:
        # 기본값을 1000으로 설정
        vbr_size = int(body.get("vbr_size", 1000))
        word = body["text"]
        response_data = r.response(word, vbr_size=vbr_size)

        if len(response_data) != 0:
            return JSONResponse({"code":200,
                                 "message":"success",
                                 "data":response_data})
        else:
            # raise HTTPException(status_code=404, detail=f"No associated words found for that word '{word}'")
            return {
                "code": 404,
                "message": f"faild: No associated words found for that word '{word}'"
            }
    except KeyError:
        logger.error(traceback.format_exc())
        logger.error(body)
        # raise HTTPException(status_code=400, detail="Request body should contain 'text' field")
        return {
            "code": 400,
            "message": f"faild: Request body should contain 'text' field"
            }
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(body)
        # raise HTTPException(status_code=500, detail=)
        return {
            "code": 500,
            "message": str(e)
            }
