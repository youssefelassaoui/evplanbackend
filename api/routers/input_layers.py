from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.services.input_layers import get_all as service_get_all
from api.dependencies import get_database
from api.models.models import TableEnum
from api.dependencies import default_authorization
from api.models.schemas.token_data import TokenData

router = APIRouter(prefix="/input-layers", tags=["Input Layers"])


@router.get("/{table}")
async def get_all(
    table: TableEnum,
    lat_ne,
    lon_ne,
    lat_so,
    lon_so,
    precision,
    db: Session = Depends(get_database),
    user: TokenData = Depends(default_authorization),
):
    try:
        float(lat_ne)
        float(lon_ne)
        float(lat_so)
        float(lon_so)
    except ValueError:
        raise HTTPException(400, "Not valid coordinates")

    try:
        valor_precision = int(precision)
        if valor_precision < 1 or valor_precision > 3:
            raise HTTPException(400, "Not valid precision range")
    except ValueError:
        raise HTTPException(400, "Not valid precision")  

    return service_get_all(
        table=table, db=db, lon_ne=lon_ne, lat_ne=lat_ne, lon_so=lon_so, lat_so=lat_so, precision=precision
    )
