from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.services.map import (
    get_area_hexagons as service_get_area_hexagons,
    register_algorithm_search as service_register_algorithm_search,
    start_algorithm_search as service_start_algorithm_search,
    get_road_hexagons as service_get_road_hexagons
)
from api.dependencies import get_database
from api.dependencies import default_authorization
from api.models.schemas.token_data import TokenData
from api.models.schemas.models import AreaSelected, RoadSelected

router = APIRouter(prefix="/map", tags=["Map"])

@router.post("/area")
async def get_hexagons_area(
    data: AreaSelected, 
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    response = None
    
    if data.type=='search':
        response = (await service_get_area_hexagons(db=db, data=data))[0]
        
    elif data.type=='algorithm':
        response = await service_register_algorithm_search(db=db, user_id=user.sub, data=data, search_type='area')
        
    elif data.type=='search_start':
        response = await service_start_algorithm_search(db=db, data=data, search_type='area')
    
    
    return response


@router.post("/road")
async def get_hexagons_road_section(
    data: RoadSelected, 
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    
    response = None
    
    if data.type=='search':
        response = (await service_get_road_hexagons(db=db, data=data))[0]
        
    elif data.type=='algorithm':
        response = await service_register_algorithm_search(db=db, user_id=user.sub, data=data, search_type='road-section')
        
    elif data.type=='search_start':
        response = await service_start_algorithm_search(db=db, data=data, search_type='road-section')
    
    
    return response