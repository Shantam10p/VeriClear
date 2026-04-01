from fastapi import APIRouter

from app.models.schemas import QueryRequest, QueryResponse
from app.orchestrator.pipeline import pipeline


router = APIRouter()


@router.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    return pipeline.run(request)
