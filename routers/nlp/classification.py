import os
import traceback
from fastapi.responses import JSONResponse
import sys
sys.path.append("./")
sys.path.append("/app/routers/nlp/nlp_util")
sys.path.append("./routers/nlp/nlp_util")
from api_classification import VideoClassification
from util.log_function import logger
from util.redis_keyvault import get_info
from dotenv import load_dotenv
# .env 파일 경로 지정
dotenv_path = os.path.join(".", '.env')
# .env 파일 로드
load_dotenv(dotenv_path)
env = get_info("dothis-fastapi-ai")

path = env.get('LAMBDA_TASK_ROOT')

if path is None:
    path = "/app"


data_path = "/app/usedata"
cache_dir = '/app/models/huggingface'
use_cuda = True if int(os.getenv('USE_CUDA', 0)) == 1 else False
vc = VideoClassification(data_path=data_path,
                    cache_dir=cache_dir,
                    use_cuda=use_cuda)

async def main(body: dict):
    required_fields = ["title", "category", "tags", "description"]

    # Check if all required fields are present in the body
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        logger.error(f"Request body should contain {', '.join(missing_fields)}")
        return {
            "code": 400,
            "message": f"faild: Request body should contain {', '.join(missing_fields)}"
        }

    try:
        title = body["title"]
        category = body["category"]
        tags = body["tags"]
        description = body["description"]

        # Assume video_cluster_respons returns a tuple (str, int, float)
        response_data = vc.response(title, category, tags, description)

        # return {
        #     "code": 200,
        #     "message": "success",
        #     "data": {
        #         "cluster_name": cluster_name,
        #         "cluster_id": cluster_id,
        #         "cluster_score": cluster_score
        #     }
        # }
        return JSONResponse({"code":200,
                                "message":"success",
                                "data":response_data})

    except KeyError:
        logger.error(traceback.format_exc())
        return {
            "code": 400,
            "message": "faild: Request body should contain 'text' field"
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        return {
            "code": 500,
            "message": str(e)
        }