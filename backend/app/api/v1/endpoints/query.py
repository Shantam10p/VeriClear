from fastapi import APIRouter


router = APIRouter()


@router.post("/query")
async def query() -> dict[str, str]:
    return {"status": "not_implemented"}
