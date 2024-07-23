from operator import or_
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import List

from api.constants import KEYCLOAK_ADMIN_ROLE
from api.dependencies import create_keycloak_admin
from api.models.models import Algorithms, Restriction, Element, EntityType, Rule, RestrictionType, ComparisonOperator, AlgorithmSearchs
from api.models.schemas.algorithm import AlgorithmIn, AlgorithmOut, AlgorithmSearchsOut
from api.models.schemas.element import ElementIn
from api.models.schemas.rule import RuleIn
from api.models.schemas.restriction import RestrictionIn
from api.services.auth import get_users_list as get_users_list_service

def create_algorithm(db: Session, user_id: str, data: AlgorithmIn):
    exist_algorithm = db.query(Algorithms).filter(Algorithms.name == data.name).count()
    if exist_algorithm:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Algorithm name exists")

    try:
        algorithm: Algorithms = Algorithms(
            name=data.name,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            is_active=data.is_active,
            is_parent=True,
        )
        db.add(algorithm)
        db.commit()
        db.refresh(algorithm)
        return algorithm
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")


def get_algorithms(db: Session, user_id: str):
    
    algorithms_db: List[Algorithms] = db.query(Algorithms).order_by(Algorithms.name).all()
    users = get_users_list_service()
    
    keycloak_admin = create_keycloak_admin()
    print(keycloak_admin.get_realm_roles_of_user(user_id=user_id))
    user_roles = keycloak_admin.get_realm_roles_of_user(user_id=user_id)
    admin_role = True if len([role for role in user_roles if role['name'] in KEYCLOAK_ADMIN_ROLE]) > 0 else False
    if admin_role:
        algorithms_db: List[Algorithms] = db.query(Algorithms).order_by(Algorithms.created_at).all()
    else:
        algorithms_db: List[Algorithms] = db.query(Algorithms).order_by(Algorithms.created_at).filter(
            or_(and_(Algorithms.is_parent==True, Algorithms.is_active==True), Algorithms.user_id==user_id))
    
    return algorithms_db_to_dto(algorithms_db, users)
    

def algorithms_db_to_dto(algorithms_db: List[Algorithms], users: List[dict]):
    return [algorithm_db_to_dto(algorithm, users) for algorithm in algorithms_db]

def algorithm_db_to_dto(algorithm: Algorithms, users: List[dict]):
    user = next((user for user in users if user["id"] == str(algorithm.user_id)), None)

    return AlgorithmOut(
        id=algorithm.id,
        name=algorithm.name,
        user_name=(user["username"] if user is not None else ""),
        is_active=algorithm.is_active,
        num_searchs=len(algorithm.searchs)
    )

def get_algorithm_by_id(db: Session, id: int):
    algorithm = db.query(Algorithms).options(
                    joinedload(Algorithms.elements)
                    .joinedload(Element.rules)
                    .joinedload(Rule.restrictions)
                ).filter(Algorithms.id == id).first()

    if algorithm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")
    return algorithm


def get_full_detail_algorithm_by_id(db: Session, id: int):
    algorithm = db.query(Algorithms).options(
                    joinedload(Algorithms.elements)
                        .joinedload(Element.rules)
                            .joinedload(Rule.restrictions)
                                .joinedload(Restriction.restriction_type),
                    joinedload(Algorithms.elements)
                        .joinedload(Element.rules)
                            .joinedload(Rule.restrictions)
                                .joinedload(Restriction.comparison_operator),          
                    joinedload(Algorithms.elements)
                        .joinedload(Element.entity_type),
                ).filter(Algorithms.id == id).first()

    if algorithm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")
    return algorithm

def edit_algorithm(db: Session, user_id: str, id: int, data: AlgorithmIn):
    try:
        algorithm: Algorithms = db.query(Algorithms).filter(Algorithms.id == id).first()
        if algorithm is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")

        exist_algorithm_name = db.query(Algorithms).filter(and_(Algorithms.name == data.name, Algorithms.id != id)).count()
        if exist_algorithm_name:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Algorithm name exists")

        algorithm.name = data.name
        algorithm.user_id = user_id
        algorithm.is_active = data.is_active
        
        db.commit()
        db.refresh(algorithm)
        return algorithm
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")
    
    
def copy_algorithm(db: Session, user_id: str, id: int):
    algorithm = get_full_detail_algorithm_by_id(db, id)
    if algorithm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")
    
    algorithm_copy: Algorithms = Algorithms(
        name=algorithm.name + " " + "(copy)",
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        is_active=algorithm.is_active,
        is_parent=False,
    )
    
    db.add(algorithm_copy)
    db.commit()
    db.refresh(algorithm_copy)
    
    for element in algorithm.elements:
        element_copy: Element = Element(
            algorithm_id=algorithm_copy.id,
            entity_type_id=element.entity_type_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=element.is_active
        )
        db.add(element_copy)
        db.commit()
        db.refresh(element_copy)
        
        for rule in element.rules:
            rule_copy: Rule = Rule(
                element_id=element_copy.id,
                score=rule.score,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                is_active=rule.is_active
            )
            db.add(rule_copy)
            db.commit()
            db.refresh(rule_copy)
            
            for restriction in rule.restrictions:
                restriction_copy: Restriction = Restriction(
                    rule_id=rule_copy.id,
                    restriction_type_id=restriction.restriction_type_id,
                    comparison_operator_id=restriction.comparison_operator_id,
                    value=restriction.value,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    is_active=restriction.is_active
                )
                db.add(restriction_copy)
                db.commit()
                db.refresh(restriction_copy)
            
    db.refresh(algorithm_copy)
    
    return algorithm_copy
    
    

def get_entity_type(db: Session):
    try:
        return db.query(EntityType).options(joinedload(EntityType.restrictions)).all()
    except SQLAlchemyError:
        raise HTTPException(503, "Query error")

def get_comparison(db: Session):
    try:
        return db.query(ComparisonOperator).all()
    except SQLAlchemyError:
        raise HTTPException(503, "Query error")

def get_searchs(db: Session):
    try:
        algorithms_searchs_db: List[AlgorithmSearchs] = db.query(AlgorithmSearchs).options(
            joinedload(AlgorithmSearchs.algorithm)
        ).order_by(AlgorithmSearchs.created_at.desc()).all()
        users = get_users_list_service()

        return algorithms_searchs_db_to_dto(algorithms_searchs_db, users)
    except SQLAlchemyError:
        raise HTTPException(503, "Query error")

def algorithms_searchs_db_to_dto(algorithms_searchs_db: List[AlgorithmSearchs], users: dict):
    return [algorithm_searchs_db_to_dto(algorithm_searchs, users) for algorithm_searchs in algorithms_searchs_db]

def algorithm_searchs_db_to_dto(algorithm_searchs: AlgorithmSearchs, users: dict):
    user = next((user for user in users if user["id"] == str(algorithm_searchs.user_id)), None)

    return AlgorithmSearchsOut(
        algorithm_id=algorithm_searchs.algorithm.id,
        algorithm=algorithm_searchs.algorithm.name,
        user_name=(user["username"] if user is not None else ""),
        location_num=algorithm_searchs.locations_num,
        polygon_size=algorithm_searchs.polygons_size,
        selection_type=algorithm_searchs.selection_type,
        created_at=algorithm_searchs.created_at,
        num_import=algorithm_searchs.num_import,
        num_export=algorithm_searchs.num_export  
    )

def update_count_export_searchs(db: Session, search_id: int):
   return update_num_searchs(db, search_id, True)

def update_count_import_searchs(db: Session, search_id: int):
   return update_num_searchs(db, search_id, False)

def update_num_searchs(db: Session, search_id: int, export: bool):
    try:
        search: AlgorithmSearchs = db.query(AlgorithmSearchs).filter(AlgorithmSearchs.id == search_id).first()
        if search is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Search not found")

        if export:
            search.num_export = search.num_export+1
        else:
            search.num_import = search.num_import+1

        db.commit()
        db.refresh(search)
        return search
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def create_element(db: Session, user_id: str, data: ElementIn):
    try:
        element: Element = Element(
            algorithm_id=data.algorithm_id,
            entity_type_id=data.entity_type_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=data.is_active
        )
        db.add(element)
        update_user_by_element(db, user_id, element)

        db.commit()
        db.refresh(element)
        return db.query(Element).filter(Element.id == element.id).first()
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def edit_element(db: Session, user_id: str, id: int, data: ElementIn):
    try:
        element: Element = db.query(Element).filter(Element.id == id).first()
        if element is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Element not found")

        element.entity_type_id = data.entity_type_id
        element.is_active = data.is_active
        element.updated_at = datetime.now(timezone.utc)
        
        update_user_by_element(db, user_id, element)

        db.commit()
        db.refresh(element)
        return element
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def update_user_by_element(db: Session, user_id: str, element: Element):
    algorithm: Algorithms = db.query(Algorithms).filter(Algorithms.id == element.algorithm_id).first()
    if algorithm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Algorithm not found")
    algorithm.user_id = user_id

def create_rule(db: Session, user_id: str, data: RuleIn):
    try:
        rule: Rule = Rule(
            element_id=data.element_id,
            score=data.score,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=data.is_active
        )
        db.add(rule)
        update_user_by_rule(db, user_id, rule)

        db.commit()
        db.refresh(rule)
        return db.query(Rule).filter(Rule.id == rule.id).first()
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def edit_rule(db: Session, user_id: str, id: int, data: RuleIn):
    try:
        rule: Rule = db.query(Rule).filter(Rule.id == id).first()
        if rule is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")

        rule.score = data.score
        rule.is_active = data.is_active
        rule.updated_at = datetime.now(timezone.utc)
        
        update_user_by_rule(db, user_id, rule)
        
        db.commit()
        db.refresh(rule)
        return rule
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def update_user_by_rule(db: Session, user_id: str, rule: Rule):
    element: Element = db.query(Element).filter(Element.id == rule.element_id).first()
    if element is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Element not found")

    element.algorithm.user_id = user_id

def create_restriction(db: Session, user_id: str, data: RestrictionIn):
    try:
        restriction: Restriction = Restriction(
            rule_id=data.rule_id,
            restriction_type_id=data.restriction_type_id,
            comparison_operator_id=data.comparison_operator_id,
            value=data.value,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=data.is_active
        )
        db.add(restriction)
        update_user_by_restriction(db, user_id, restriction)

        db.commit()
        db.refresh(restriction)
        return db.query(Restriction).filter(Restriction.id == restriction.id).first()
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def edit_restriction(db: Session, user_id: str, id: int, data: RestrictionIn):
    try:
        restriction: Restriction = db.query(Restriction).filter(Restriction.id == id).first()
        if restriction is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Restriction not found")

        restriction.restriction_type_id = data.restriction_type_id
        restriction.comparison_operator_id = data.comparison_operator_id
        restriction.value = data.value
        restriction.is_active = data.is_active
        restriction.updated_at = datetime.now(timezone.utc)
        
        update_user_by_restriction(db, user_id, restriction)
        
        db.commit()
        db.refresh(restriction)
        return restriction
    except SQLAlchemyError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Query error")

def update_user_by_restriction(db: Session, user_id: str, restriction: Restriction):
    rule: Rule = db.query(Rule).filter(Rule.id == restriction.rule_id).first()    
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")
    rule.element.algorithm.user_id = user_id
