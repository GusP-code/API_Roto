from fastapi import APIRouter, HTTPException, Query
from config.settings import settings
from services.data_service import DataService
from models.data_model import ResponseModel, SetModel

router = APIRouter(prefix=settings.API_V1_STR)


@router.get("/data", response_model=ResponseModel)
async def get_complete_data(
    set_id: str = Query(..., description="ID del set"),
    width: int = Query(..., description="Ancho en mm"),
    height: int = Query(..., description="Alto en mm"),
    include_schraube: bool = Query(False, description="Incluir artículos Schraube")
):
    try:
        return DataService.get_complete_data(set_id, width, height, include_schraube)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sets", response_model=list[SetModel])
async def list_sets():
    try:
        return DataService.list_sets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
