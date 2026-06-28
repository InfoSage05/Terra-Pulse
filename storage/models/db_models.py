from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON, DateTime, UniqueConstraint, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Area(Base):
    __tablename__ = 'areas'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area_type = Column(String, nullable=False)
    county = Column(String, nullable=False)
    geometry = Column(Geometry('POLYGON', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PropertySale(Base):
    __tablename__ = 'property_sales'
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), index=True)
    sale_date = Column(Date, nullable=False, index=True)
    price_eur = Column(Float, nullable=False)
    address_raw = Column(String, nullable=False)
    address_normalized = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    source_name = Column(String, nullable=False)
    source_record_id = Column(String)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('sale_date', 'address_raw', 'price_eur', name='uq_property_sales_date_address_price'),
    )

class Amenity(Base):
    __tablename__ = 'amenities'
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), index=True)
    amenity_type = Column(String, nullable=False, index=True)
    name = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    osm_id = Column(Integer)
    source_name = Column(String, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('osm_id', 'amenity_type', name='uq_amenities_osmid_type'),
    )

class AreaDemographics(Base):
    __tablename__ = 'area_demographics'
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), index=True)
    year = Column(Integer, nullable=False)
    population = Column(Integer)
    population_density = Column(Float)
    deprivation_index = Column(Float)
    age_profile_json = Column(JSON)
    source_name = Column(String, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('area_id', 'year', name='uq_demographics_area_year'),
    )

class CrimeStat(Base):
    __tablename__ = 'crime_stats'
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), index=True)
    garda_division = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    crime_category = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    source_name = Column(String, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('area_id', 'garda_division', 'year', 'crime_category', name='uq_crime_stats_area_div_year_cat'),
    )

class AreaAgentSummary(Base):
    __tablename__ = 'area_agent_summaries'
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), index=True)
    run_id = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    livability_signal = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    flags = Column(JSON)
    needs_human_review = Column(Boolean, server_default='false')
    structured_data_snapshot = Column(JSON)
    source_count = Column(Integer, nullable=False)
    model_name = Column(String, nullable=False)
    source_name = Column(String, nullable=False, server_default='agent_pipeline')
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

