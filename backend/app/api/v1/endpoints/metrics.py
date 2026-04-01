from fastapi import APIRouter


router = APIRouter()


@router.get("/metrics")
async def get_metrics() -> dict[str, str]:
    return {"status": "not_implemented"}
