import asyncio
import time
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from fastapi import HTTPException, status
import math
import json
from typing import List
from datetime import datetime, timezone
from pandas.core.series import Series
import geopandas as gpd
import random

from api.models.schemas.models import AreaSelected, RoadSelected
from api.models.models import Algorithms, AlgorithmSearchs, Element, Rule
from api.constants import COORDINATE_SYSTEM
from api.services.algorithms import get_full_detail_algorithm_by_id
from api.routers.websocket import send_message



async def get_area_hexagons(data: AreaSelected, db: Session):

    query_area_meters: str = text(
        """SELECT ST_Area(
            ST_GeomFromGeoJSON('{}')::geography
        )""".format(data.geometry.json())
    )
    result_area_meters = db.execute(query_area_meters).fetchone()    
    side_hexagons_meters = math.sqrt(0.3849*result_area_meters[0]/data.num_hexagons) # 2/3√3 = 0.3849

    query: str = text(
        """WITH my_geom AS 
            (SELECT ST_GeomFromGeoJSON('{}') AS geom1 )
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(g.geom)::json,
                'properties', row_to_json(g)::jsonb-'geom'
                )
            )
        )
        FROM 
            (SELECT ROW_NUMBER() OVER () AS id, hex as geom, ST_X(ST_Centroid(hex)) as centroid_x, ST_Y(ST_Centroid(hex)) as centroid_y
                FROM my_geom, -- SRS 4326
                    ST_Transform(my_geom.geom1, {}) AS my_geom_meter, -- SRS 25830 (EU)
                    ST_HexagonGrid({}, my_geom_meter) AS hex_meter, -- SRS 25830 (EU)
                    ST_Transform(hex_meter.geom, 4326) AS hex-- SRS 4326
                        WHERE ST_Intersects(my_geom.geom1, hex)
            ) g
        """.format(data.geometry.json(), COORDINATE_SYSTEM if COORDINATE_SYSTEM is not None else '3857', side_hexagons_meters)
    )
    result = db.execute(query)
    data_result = result.mappings().first()["json_build_object"]

    return data_result, side_hexagons_meters



async def get_road_hexagons(data: RoadSelected, db: Session):
    
    query_buffer: str = text(
        """WITH my_geom AS 
            (
                SELECT ST_Buffer(
                    ST_Union(
                        ARRAY[{}]
                    )::geography, {}, 'endcap=flat join=mitre mitre_limit=5.0'
                )::geometry as geom1
            )
        """.format(",".join([f"ST_GeomFromGeoJSON('{geom.json()}')" for geom in data.geometries]), data.distance_buffer)
    )

    query_area_meters: str = text(
        """{}
            SELECT ST_Area(my_geom.geom1::geography)
                FROM my_geom""".format(query_buffer)
    )
    result_area_meters = db.execute(query_area_meters).fetchone()    
    side_hexagons_meters = math.sqrt(0.3849*result_area_meters[0]/data.num_hexagons) # 2/3√3 = 0.3849

    query: str = text(
        """{}
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(g.geom)::json,
                'properties', row_to_json(g)::jsonb-'geom'
                )
            )
        )
        FROM 
            (SELECT ROW_NUMBER() OVER () AS id, hex as geom, ST_X(ST_Centroid(hex)) as centroid_x, ST_Y(ST_Centroid(hex)) as centroid_y
                FROM my_geom, -- SRS 4326
                    ST_Transform(my_geom.geom1, {}) AS my_geom_meter, -- SRS 25830 (EU)
                    ST_HexagonGrid({}, my_geom_meter) AS hex_meter, -- SRS 25830 (EU)
                    ST_Transform(hex_meter.geom, 4326) AS hex-- SRS 4326
                        WHERE ST_Intersects(my_geom.geom1, hex)
            ) g
        """.format(query_buffer, COORDINATE_SYSTEM if COORDINATE_SYSTEM is not None else '3857', side_hexagons_meters)
    )

    result = db.execute(query)
    data_result = result.mappings().first()["json_build_object"]

    return data_result, side_hexagons_meters



async def register_algorithm_search(data: AreaSelected, db: Session, user_id: str, search_type: str):
    # Check if the used algorithm exists
    algorithm = check_exist_algorithm(db, data.id)
    
    # Execute hexagons query
    if search_type == 'area':
        area_hexagons, side_hexagons_meters = await get_area_hexagons(data, db)
    elif search_type == 'road-section':
        area_hexagons, side_hexagons_meters = await get_road_hexagons(data, db)
    
    # Get hexagons
    hexagons = gpd.GeoDataFrame.from_features(area_hexagons)
    
    # Save algorithm search in db
    algorithm_search: AlgorithmSearchs = AlgorithmSearchs(
        user_id=user_id,
        algorithm_id=algorithm.id,
        locations_num=len(hexagons),
        polygons_size=side_hexagons_meters,
        selection_type=search_type,
        created_at=datetime.now(timezone.utc),
        num_import=0,
        num_export=0
    )
    algorithm_search_id = save_algorithm_search(db, algorithm_search)

    # Retrun algorithm id to subscribe websocket front
    return algorithm_search_id
    
    
async def start_algorithm_search(data, db: Session, search_type: str):
    # Check if the algorithm search exists
    algorithm_search = check_exist_algorithm_search(db, data.id)
    
    # Execute hexagons query
    if search_type == 'area':
        area_hexagons, side_hexagons_meters = await get_area_hexagons(data, db)
    elif search_type == 'road-section':
        area_hexagons, side_hexagons_meters = await get_road_hexagons(data, db)
    
    # Get hexagons
    hexagons = gpd.GeoDataFrame.from_features(area_hexagons)
    
    # Get full detailed algorithm with relations
    algorithm = get_full_detail_algorithm_by_id(db=db, id=algorithm_search.algorithm_id)
    
    # Create async process to apply algorithm and return data to front using websocket
    asyncio.create_task(apply_search(db, algorithm, algorithm_search.id, hexagons))
    
    # Retrun algorithm id to subscribe websocket front
    return "OK"


def check_exist_algorithm(db: Session, algorithm_id: int):
    algorithm: Algorithms = db.query(Algorithms).filter(Algorithms.id == algorithm_id).first()
    if algorithm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")
    return algorithm

def check_exist_algorithm_search(db: Session, algorithm_search_id: int):
    algorithm_search: AlgorithmSearchs = db.query(AlgorithmSearchs).filter(AlgorithmSearchs.id == algorithm_search_id).first()
    if algorithm_search is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm search not found")
    return algorithm_search


def get_data_script(data: Series):
    point_data =  {
        "id":data['id'],
        "coordinates": {
            "longitude": data['centroid_x'],
            "latitude": data['centroid_y']
        },
        "score": None
    }
    return point_data

def save_algorithm_search(db: Session, algorithm_search: AlgorithmSearchs):
    db.add(algorithm_search)
    db.commit()
    db.refresh(algorithm_search)
    return algorithm_search.id


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]
    
    

async def apply_search(db: Session, algorithm, algorithm_search_id, hexagons):
    # REPLACE BY SCRIPT TO CALCULATE PUNTUATION
    # Se va a analizar punto a punto cada hexágono de recibido
    for i in range(0, len(hexagons)):
        # accedemos al hexágono a analizar
        hexagon = hexagons[hexagons['id'] == i+1]
        
        # transformamos el hexágono a un objeto con id, score y coordenadas del centro
        point_data = get_data_script(hexagons.loc[i])
        
        # al comienzo el punto tiene una puntuación de 0
        point_data_score = 0
        
        # obtenemos la lista de elementos activos del algoritmo
        active_elements = [element for element in algorithm.elements if element.is_active is True]
        
        # recorremos los elementos del algoritmo
        for element in active_elements:
            # obtenemos el nombre de la tabla sobre el que vamos a ejecutar la query
            element_table_name = element.entity_type.table_name
            
            # ordenamos las reglas del elemento en base a la puntuación para ir de menos a más restrictivas
            active_rules = [rule for rule in element.rules if rule.is_active==True]
            ordered_rules = sorted(active_rules, key=lambda d: d.score, reverse=False) 
            
            # si el hexágono no cumple las restricciones de la regla con menos score, 
            # el score será 0 y no seguimos buscando reglas para este hexágono en este elemento
            stop_search = False
            matched_rule = None
            i=0
            while not stop_search and i<len(ordered_rules):
                # obtenemos la regla
                rule = ordered_rules[i]
                
                # obtenemos las restricciones activas
                active_restrictions = [restriction for restriction in rule.restrictions if restriction.is_active==True]
                
                # comprobamos que todas las restricciones se cumplen
                restrictions_matched = check_restrictions_match(db, element_table_name, active_restrictions, point_data)
                
                # asociamos a matched_rule la regla si esta cumple las restricciones
                matched_rule = rule if restrictions_matched else matched_rule
                
                # si es la primera restricción (menos restrictiva) y no se han cumplido las restricciones, dejamos de buscar
                if i==0 and not restrictions_matched:
                    stop_search = True
                
                i+=1
            
            point_data_score += matched_rule.score if matched_rule else 0
        
        point_data['score'] = point_data_score

        score = gpd.GeoDataFrame([point_data])[['id', 'score']]

        result = gpd.GeoDataFrame.merge(hexagon, score, on='id', how='left')
        
        result_json = result.to_json()
        await send_message(str(algorithm_search_id), result_json)

def check_restrictions_match(db:Session, table_name, restrictions, point_data):
    i=0
    query = 'SELECT * FROM "'+table_name+'" '
    for restriction in restrictions:
        query += 'WHERE ' if i==0 else 'AND '
        
        if restriction.restriction_type.name in ['linear_distance']:
            query += """
                        ST_DWithin(ST_SetSRID(geom, 4326)::geography, 
                        ST_GeomFromText('POINT({} {})', 4326)::geography, 
                        {})                        
                        """.format(
                                        point_data['coordinates']['longitude'],
                                        point_data['coordinates']['latitude'],
                                        restriction.value
                                        )
        else:
            query += """{} {} {} """.format(
                                            restriction.restriction_type.name,
                                            restriction.comparison_operator.symbol,
                                            restriction.value
                                            )
        i+=1
    
    query_str = text(query)
    
    result = db.execute(query_str)
    
    return True if result.mappings().first() else False


def get_match_linear_distance(db:Session, table_name, point_lon, point_lat, distance):
    query: str = text(
            """
                SELECT 
                    gid
                FROM 
                    \"{}\" 
                WHERE 
                    ST_DWithin(
                        ST_SetSRID(geom, 4326)::geography, 
                        ST_GeomFromText('POINT({} {})', 4326)::geography, 
                        {}
                    )
                LIMIT 
                    1
                 """.format(
                table_name, point_lon, point_lat, distance
            )
        )
    
    """
            SELECT 
                COUNT(*) 
            FROM 
                "locations"
            WHERE (
                ST_DWithin(
                    ST_SetSRID(ST_MakeLine(
                        ARRAY[
                            ST_MakePoint(2.1736, 41.38518) <... redacted, approx 200 points> ST_MakePoint(73.31681999999995, 55.05574999999999)
                        ]
                    ), 4326),locations.geom,0.26
                )
                )
                AND (ST_DWithin(
                ST_SetSRID(ST_MakeLine(
                ARRAY[
                    ST_MakePoint(2.1736, 41.38518) <... redacted, approx 200 points> ST_MakePoint(73.31681999999995, 55.05574999999999)
                ]
                )
                , 4326)::geography,
                locations.geog,
                5000,
                false
                )
                );
                """
    result = db.execute(query)
    
    return True if result.mappings().first() else False


def get_match_linear_distance1(db:Session, table_name, point_lon, point_lat, distance):
    query: str = text(
            """SELECT count(gid)
                FROM \"{}\" 
                WHERE 
                    ST_DWithin(ST_SetSRID(geom, 4326)::geography, 
                    ST_GeomFromText('POINT({} {})', 4326)::geography, 
                    {})
                LIMIT 1
                 """.format(
                table_name, point_lon, point_lat, distance
            )
        )
    result = db.execute(query)
    
    return True if result.mappings().first()['count']>0 else False


def get_match_linear_distance2(db:Session, table_name, point_lon, point_lat, distance):
    query: str = text(
            """SELECT gid
                FROM \"{}\" 
                WHERE 
                    ST_DistanceSphere(geom, ST_MakePoint({},{})) <= {} * 1609.34
                LIMIT 1
                 """.format(
                table_name, point_lon, point_lat, (int(distance)/1000)
            )
        )
    
            
    result = db.execute(query)
    return True if result.mappings().first() else False