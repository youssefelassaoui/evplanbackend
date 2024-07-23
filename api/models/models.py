# coding: utf-8
from sqlalchemy import Column, Float, Integer, Numeric, String, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from geoalchemy2 import Geometry
from enum import Enum
from typing import List

from api.database import Base

entity_restriction = Table(
    'algorithm_entity_types_restriction_types', 
    Base.metadata,
    Column('entity_type', ForeignKey('algorithm_entity_types.id'), primary_key=True),
    Column('restriction_type', ForeignKey('algorithm_rule_restriction_types.id'), primary_key=True)
)

class Algorithms(Base):
    __tablename__ = "algorithms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True))
    user_id = Column(UUID)
    is_active = Column(Boolean, nullable =False)
    is_parent = Column(Boolean, nullable =False)
    elements: Mapped[List["Element"]] = relationship("Element", back_populates="algorithm")
    searchs: Mapped[List["AlgorithmSearchs"]] = relationship("AlgorithmSearchs", back_populates="algorithm")
    

class EntityType(Base):
    __tablename__ = "algorithm_entity_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    table_name = Column(String(50))

    elements: Mapped[List["Element"]] = relationship("Element", back_populates="entity_type")
    restrictions: Mapped[List["RestrictionType"]] = relationship("RestrictionType", secondary=entity_restriction, back_populates="entities")

class Element(Base):
    __tablename__ = "algorithm_elements"

    id = Column(Integer, primary_key=True, index=True)
    algorithm_id = Column(ForeignKey("algorithms.id"), nullable=False)
    entity_type_id = Column(ForeignKey("algorithm_entity_types.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable =False)

    algorithm: Mapped["Algorithms"] = relationship("Algorithms", back_populates="elements")
    entity_type: Mapped["EntityType"] = relationship("EntityType", back_populates="elements")
    rules: Mapped[List["Rule"]] = relationship("Rule", back_populates="element")

class Rule(Base):
    __tablename__ = "algorithm_element_rules"

    id = Column(Integer, primary_key=True, index=True)
    element_id = Column(ForeignKey("algorithm_elements.id"), nullable=False)
    score = Column(Float(53), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable =False)

    element: Mapped["Element"] = relationship("Element", back_populates="rules")
    restrictions: Mapped[List["Restriction"]] = relationship("Restriction", back_populates="rule")

class RestrictionType(Base):
    __tablename__ = "algorithm_rule_restriction_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    data_type = Column(String(20))

    entities: Mapped[List["EntityType"]] = relationship("EntityType", secondary=entity_restriction, back_populates="restrictions")
    restrictions: Mapped[List["Restriction"]] = relationship("Restriction", back_populates="restriction_type")

class ComparisonOperator(Base):
    __tablename__ = "algorithm_comparison_operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    symbol = Column(String(5), nullable=False)
    
    restrictions: Mapped[List["Restriction"]] = relationship("Restriction", back_populates="comparison_operator")

class Restriction(Base):
    __tablename__ = "algorithm_rule_restrictions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(ForeignKey("algorithm_element_rules.id"), nullable=False)
    restriction_type_id = Column(ForeignKey("algorithm_rule_restriction_types.id"), nullable=False)
    comparison_operator_id = Column(ForeignKey("algorithm_comparison_operators.id"), nullable=False)
    value = Column(String(50))
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable =False)

    rule: Mapped["Rule"] = relationship("Rule", back_populates="restrictions")
    restriction_type: Mapped["RestrictionType"] = relationship("RestrictionType", back_populates="restrictions")
    comparison_operator: Mapped["ComparisonOperator"] = relationship("ComparisonOperator", back_populates="restrictions")

class AlgorithmSearchs(Base):
    __tablename__ = "algorithm_searchs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID)
    algorithm_id = Column(ForeignKey("algorithms.id"), nullable=False)
    locations_num = Column(Integer)
    polygons_size = Column(Integer)
    selection_type = Column(String(20))
    created_at = Column(DateTime(timezone=True), nullable=False)
    num_import = Column(Integer, nullable=False)
    num_export = Column(Integer, nullable=False)

    algorithm: Mapped["Algorithms"] = relationship("Algorithms", back_populates="searchs")

class ElectricalNetwork(Base):
    __tablename__ = "electrical network"

    gid = Column(Integer, primary_key=True, index=True)
    full_id = Column(String(254), nullable=True)
    osm_id = Column(String(254), nullable=True)
    osm_type = Column(String(254), nullable=True)
    power = Column(String(254), nullable=True)
    n = Column(String(254), nullable=True)
    barrier = Column(String(254), nullable=True)
    circuits = Column(String(254), nullable=True)
    wires = Column(String(254), nullable=True)
    frequency = Column(String(254), nullable=True)
    cables = Column(String(254), nullable=True)
    voltage = Column(String(254), nullable=True)
    substation = Column(String(254), nullable=True)
    name = Column(String(254), nullable=True)
    location = Column(String(254), nullable=True)
    geom = Column(Geometry("MULTILINESTRING"), index=True)

#done
class FuelStation(Base):
    __tablename__ = "fuel stations"

    gid = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String(12), nullable=True)
    code = Column(Integer, nullable=True)
    fclass = Column(String(28), nullable=True)
    name = Column(String(100), nullable=True)
    geom = Column(Geometry("MULTILINESTRING"), index=True)

#done
class Municipality(Base):
    __tablename__ = "communes"

    gid = Column(Integer, primary_key=True, index=True)
    objectid = Column(Float, nullable=True)
    type_commu = Column(String(5), nullable=True)
    code_commu = Column(String(50), nullable=True)
    nom_commun = Column(String(50), nullable=True)
    nom_comm_1 = Column(String(50), nullable=True)
    nb_menages = Column(Float, nullable=True)
    population = Column(Float, nullable=True)
    etrangers = Column(Float, nullable=True)
    marocains = Column(Float, nullable=True)
    code_provi = Column(String(50), nullable=True)
    code_regio = Column(String(50), nullable=True)
    code_com_o = Column(String(50), nullable=True)
    nom_com_ol = Column(String(150), nullable=True)
    shape__are = Column(Numeric, nullable=True)
    shape__len = Column(Numeric, nullable=True)
    geom = Column(Geometry("MULTIPOLYGON"), index=True)


#done
class RoadNetwork(Base):
    __tablename__ = "road network"

    gid = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String(12), nullable=True)
    code = Column(Integer, nullable=True)
    fclass = Column(String(28), nullable=True)
    name = Column(String(100), nullable=True)
    ref = Column(String(20), nullable=True)
    oneway = Column(String(1), nullable=True)
    maxspeed = Column(Integer, nullable=True)
    layer = Column(Float, nullable=True)
    bridge = Column(String(1), nullable=True)
    tunnel = Column(String(1), nullable=True)
    geom = Column(Geometry("MULTILINESTRING"), index=True)


#done 
class EvChargingStation(Base):
    __tablename__ = "ev_stations"

    gid = Column(Integer, primary_key=True, index=True)
    creation_d = Column(String(24), nullable=True)
    name = Column(String(254), nullable=True)
    address = Column(String(254), nullable=True)
    power = Column(Float, nullable=True)
    voltage = Column(Float, nullable=True)
    connector_ = Column(String(254), nullable=True)
    quantity = Column(Float, nullable=True)
    id = Column(Numeric, nullable=True)
    geom = Column(Geometry("MULTIPOINT"), index=True)

#done
class Substations(Base):
    __tablename__ = "substations"

    gid = Column(Integer, primary_key=True, index=True)
    id = Column(Float, nullable=True)
    power = Column(String(254), nullable=True)
    constructi = Column(String(254), nullable=True)
    barrier = Column(String(254), nullable=True)
    voltage = Column(String(254), nullable=True)
    substation = Column(String(254), nullable=True)
    name = Column(String(254), nullable=True)
    location = Column(String(254), nullable=True)
    geom = Column(Geometry("MULTIPOINT"), index=True)

#done
class Province(Base):
    __tablename__ = "provinces"

    gid = Column(Integer, primary_key=True, index=True)
    objectid = Column(Float, nullable=True)
    code_provi = Column(String(50), nullable=True)
    population = Column(Numeric, nullable=True)
    menages = Column(Numeric, nullable=True)
    etrangers = Column(Numeric, nullable=True)
    marocains = Column(Numeric, nullable=True)
    nom_provin = Column(String(150), nullable=True)
    code_regio = Column(String(6), nullable=True)
    superficie = Column(Numeric, nullable=True)
    shape__are = Column(Numeric, nullable=True)
    shape__len = Column(Numeric, nullable=True)
    geom = Column(Geometry("MULTIPOINT"), index=True)


INPUT_LAYERS = [
    {
        "name": "electrical-network",
        "description": "Electrical Network KPI",
        "table_name": ElectricalNetwork.__tablename__,
    },
    {
        "name": "fuel-stations",
        "description": "Fuel Stations KPI",
        "table_name": FuelStation.__tablename__,
    },
    {
        "name": "municipality",
        "description": "Municipalities KPI",
        "table_name": Municipality.__tablename__
    },
    {
        "name": "road-network",
        "description": "Road Network KPI",
        "table_name": RoadNetwork.__tablename__,
    },
    {
        "name": "ev-charging-stations",
        "description": "EV Charging Stations KPI",
        "table_name": EvChargingStation.__tablename__,
    },
    {
        "name": "substations",
        "description": "Substations KPI",
        "table_name": Substations.__tablename__
    },
    {
        "name": "province",
        "description": "Province KPI",
        "table_name": Province.__tablename__
    }
]

TableEnum = Enum(
    "TableEnum",
    {tn: tn.lower() for tn in [table["name"] for table in INPUT_LAYERS]},
    type=str,
)
