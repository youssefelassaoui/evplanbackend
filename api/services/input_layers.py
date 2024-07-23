from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.models.models import INPUT_LAYERS


def get_all(
    table: str, lon_ne: float, lat_ne: float, lon_so: float, lat_so: float, precision: int, db: Session
):
    table_name = [t["table_name"] for t in INPUT_LAYERS if t["name"] == table]
    if table_name is None or len(table_name) == 0:
        raise HTTPException(
            status_code=404, detail="No data found for current input layer"
        )

    query: str = text(
        """SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(d.geom)::json,
                'properties', row_to_json(d)::jsonb-'geom'
                )
            )
            )
            FROM (SELECT c.geom, c.gid
                FROM \"{}\" c
                where ST_Intersects(ST_SetSRID(c.geom,4326), ST_MakeEnvelope({},{},{},{}, 4326))
            ) as d;""".format(
            table_name[0], lon_ne, lat_ne, lon_so, lat_so
        )
    )

    if(table == 'road-network'):
        if(int(precision) == 1):
            query = text(str(query).replace('SELECT c.geom', 'SELECT ST_Simplify(c.geom, 0.001) as geom'))

        if(int(precision) == 1 or int(precision) == 2):
            query = text(str(query).replace(', 4326))',', 4326)) and (c.fclass = \'primary\' or c.fclass = \'secondary\' or c.fclass = \'tertiary\')'))

    result = db.execute(query)
    return result.mappings().first()["json_build_object"]