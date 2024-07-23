from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.dependencies import get_database
from api.dependencies import default_authorization, admin_authorization
from api.services import algorithms as algorithms_service
from api.models.schemas.token_data import TokenData
from api.models.schemas.algorithm import AlgorithmIn
from api.models.schemas.element import ElementIn
from api.models.schemas.rule import RuleIn
from api.models.schemas.restriction import RestrictionIn

router = APIRouter(prefix="/algorithms", tags=["Algorithms"])

@router.get("")
async def get_algorithms(
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.get_algorithms(db=db, user_id=user_id)

@router.get("/entity")
async def get_entity_type(
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    return algorithms_service.get_entity_type(db=db)

@router.get("/comparison")
async def get_comparison(
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    return algorithms_service.get_comparison(db=db)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_algorithm(
    data: AlgorithmIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(admin_authorization)
):
    user_id = user.sub
    return algorithms_service.create_algorithm(db=db, user_id=user_id, data=data)

@router.post("/{id}/copy")
async def copy_algorithm(
    id: int,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.copy_algorithm(db=db, user_id=user_id, id=id)

@router.get("/searchs")
async def get_searchs(
    db: Session = Depends(get_database),
    user: TokenData = Depends(admin_authorization)
):
    return algorithms_service.get_searchs(db=db)

@router.put("/searchs/export/{search_id}")
async def update_count_export_searchs(
    search_id: int,
    db: Session = Depends(get_database)
):
    return algorithms_service.update_count_export_searchs(db=db, search_id=search_id)

@router.put("/searchs/import/{search_id}")
async def update_count_import_searchs(
    search_id: int,
    db: Session = Depends(get_database)
):
    return algorithms_service.update_count_import_searchs(db=db, search_id=search_id)

@router.get("/{id}")
async def get_algorithm_by_id(
    id: int,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    return algorithms_service.get_algorithm_by_id(db=db, id=id)

@router.put("/{id}")
async def edit_algorithm(
    id: int,
    data: AlgorithmIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.edit_algorithm(db=db, user_id=user_id, id=id, data=data)

@router.post("/element")
async def create_element(
    data: ElementIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.create_element(db=db, user_id=user_id, data=data)

@router.put("/element/{id}")
async def edit_element(
    id: int,
    data: ElementIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.edit_element(db=db, user_id=user_id, id=id, data=data)

@router.post("/rule")
async def create_rule(
    data: RuleIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.create_rule(db=db, user_id=user_id, data=data)

@router.put("/rule/{id}")
async def edit_rule(
    id: int,
    data: RuleIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.edit_rule(db=db, user_id=user_id, id=id, data=data)

@router.post("/restriction")
async def create_restriction(
    data: RestrictionIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.create_restriction(db=db, user_id=user_id, data=data)

@router.put("/restriction/{id}")
async def edit_restriction(
    id: int,
    data: RestrictionIn,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization)
):
    user_id = user.sub
    return algorithms_service.edit_restriction(db=db, user_id=user_id, id=id, data=data)