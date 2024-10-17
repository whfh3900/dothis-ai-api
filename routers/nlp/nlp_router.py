from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from routers.nlp import classification, related, channel_similer, verb
from util.log_function import logger

router = APIRouter(prefix="/nlp", tags=["nlp"])
class SetPrefix(BaseModel):
    parmeter: str = "parmeter"
    
class VerbTest(BaseModel):
    related: str = "related"
    keyword: str = "keyword"

class RelatedTest(BaseModel):
    text: str = "text"
    vbr_size: int = 1000  # 기본값을 1000으로 설정

class ClassificationTest(BaseModel):
    title: str = "title"
    tags: str = "tags"
    description: str = "description"
    category: str = "category"

class ChannelSimilerTest(BaseModel):
    ntop: int = 10
    channel_id: str = "channel_id"
    cluster: int = 0
    subscribers: int = 0
    keywords: str = ""
    tags: str = ""


@router.post("/verb")
async def verb_test(body: VerbTest):
    logger.info(f"Received verb request with body: {body}")
    try:
        body = body.dict()
        result = await verb.main(body)
        
    except Exception as e:
        logger.error(f"An error occurred in verb: {str(e)}")
    return result
        
@router.post("/related")
async def related_test(body: RelatedTest):
    logger.info(f"Received related request with body: {body}")
    try:
        body = body.dict()
        result = await related.main(body)
        
    except Exception as e:
        logger.error(f"An error occurred in related: {str(e)}")
    return result
    
@router.post("/classification")
async def classification_test(body: ClassificationTest):
    logger.info(f"Received classification request with body: {body}")
    try:
        body = body.dict()
        result = await classification.main(body)
        
    except Exception as e:
        logger.error(f"An error occurred in classification: {str(e)}")
    return result

@router.post("/channelsimiler")
async def channel_similer_test(body: ChannelSimilerTest):
    logger.info(f"Received channel similer request with body: {body}")
    try:
        body = body.dict()
        result = await channel_similer.main(body)
        
    except Exception as e:
        logger.error(f"An error occurred in channel similer: {str(e)}")
    return result