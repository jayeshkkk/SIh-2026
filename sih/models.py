"""
NER Logistics Accessibility Intelligence Platform - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()


class District(db.Model):
    __tablename__ = 'districts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    population = db.Column(db.Integer, default=0)
    connectivity_status = db.Column(db.String(20), default='normal')
    road_count = db.Column(db.Integer, default=0)
    bridge_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'lat': self.lat,
            'lng': self.lng,
            'population': self.population,
            'connectivity_status': self.connectivity_status,
            'road_count': self.road_count,
            'bridge_count': self.bridge_count,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class RoadSegment(db.Model):
    __tablename__ = 'road_segments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    from_lat = db.Column(db.Float, nullable=False)
    from_lng = db.Column(db.Float, nullable=False)
    to_lat = db.Column(db.Float, nullable=False)
    to_lng = db.Column(db.Float, nullable=False)
    road_type = db.Column(db.String(50), default='state_highway')
    length_km = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='open')
    condition = db.Column(db.String(20), default='good')
    terrain_type = db.Column(db.String(50), default='hilly')
    risk_score = db.Column(db.Float, default=0.0)
    last_inspection = db.Column(db.DateTime)
    block_reason = db.Column(db.String(200))
    block_since = db.Column(db.DateTime)
    estimated_reopen = db.Column(db.DateTime)
    weather_impact = db.Column(db.String(50), default='none')
    traffic_level = db.Column(db.String(20), default='normal')
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'from_lat': self.from_lat,
            'from_lng': self.from_lng,
            'to_lat': self.to_lat,
            'to_lng': self.to_lng,
            'road_type': self.road_type,
            'length_km': self.length_km,
            'status': self.status,
            'condition': self.condition,
            'terrain_type': self.terrain_type,
            'risk_score': self.risk_score,
            'last_inspection': self.last_inspection.isoformat() if self.last_inspection else None,
            'block_reason': self.block_reason,
            'block_since': self.block_since.isoformat() if self.block_since else None,
            'estimated_reopen': self.estimated_reopen.isoformat() if self.estimated_reopen else None,
            'weather_impact': self.weather_impact,
            'traffic_level': self.traffic_level,
            'district_id': self.district_id
        }


class Bridge(db.Model):
    __tablename__ = 'bridges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    length_m = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='operational')
    condition = db.Column(db.String(20), default='good')
    load_capacity_tons = db.Column(db.Float, default=20.0)
    built_year = db.Column(db.Integer)
    last_inspection = db.Column(db.DateTime)
    river_name = db.Column(db.String(100))
    risk_score = db.Column(db.Float, default=0.0)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lat': self.lat,
            'lng': self.lng,
            'length_m': self.length_m,
            'status': self.status,
            'condition': self.condition,
            'load_capacity_tons': self.load_capacity_tons,
            'built_year': self.built_year,
            'last_inspection': self.last_inspection.isoformat() if self.last_inspection else None,
            'river_name': self.river_name,
            'risk_score': self.risk_score,
            'district_id': self.district_id
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), default='truck')
    cargo_type = db.Column(db.String(50), default='general')
    cargo_description = db.Column(db.String(200))
    capacity_kg = db.Column(db.Float, default=5000.0)
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    speed_kmh = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    eta = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    route_polyline = db.Column(db.Text)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_number': self.vehicle_number,
            'vehicle_type': self.vehicle_type,
            'cargo_type': self.cargo_type,
            'cargo_description': self.cargo_description,
            'capacity_kg': self.capacity_kg,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'status': self.status,
            'speed_kmh': self.speed_kmh,
            'heading': self.heading,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'origin': self.origin,
            'destination': self.destination,
            'eta': self.eta.isoformat() if self.eta else None,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'route_polyline': self.route_polyline,
            'district_id': self.district_id
        }


class FieldReport(db.Model):
    __tablename__ = 'field_reports'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200))
    photo_url = db.Column(db.String(500))
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    reported_by = db.Column(db.String(100))
    reporter_phone = db.Column(db.String(20))
    reporter_designation = db.Column(db.String(100))
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String(100))
    verified_at = db.Column(db.DateTime)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'report_type': self.report_type,
            'title': self.title,
            'description': self.description,
            'lat': self.lat,
            'lng': self.lng,
            'location_name': self.location_name,
            'photo_url': self.photo_url,
            'severity': self.severity,
            'status': self.status,
            'reported_by': self.reported_by,
            'reporter_phone': self.reporter_phone,
            'reporter_designation': self.reporter_designation,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None,
            'verified': self.verified,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'district_id': self.district_id
        }


class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    location_name = db.Column(db.String(200))
    affected_districts = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    source = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'lat': self.lat,
            'lng': self.lng,
            'location_name': self.location_name,
            'affected_districts': self.affected_districts,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'source': self.source
        }


class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    location_name = db.Column(db.String(100))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall_mm = db.Column(db.Float, default=0.0)
    wind_speed = db.Column(db.Float, default=0.0)
    visibility_km = db.Column(db.Float, default=10.0)
    weather_condition = db.Column(db.String(50), default='clear')
    flood_risk = db.Column(db.String(20), default='low')
    landslide_risk = db.Column(db.String(20), default='low')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    forecast_24h = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'district_id': self.district_id,
            'location_name': self.location_name,
            'lat': self.lat,
            'lng': self.lng,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'rainfall_mm': self.rainfall_mm,
            'wind_speed': self.wind_speed,
            'visibility_km': self.visibility_km,
            'weather_condition': self.weather_condition,
            'flood_risk': self.flood_risk,
            'landslide_risk': self.landslide_risk,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'forecast_24h': self.forecast_24h
        }


class RouteHistory(db.Model):
    __tablename__ = 'route_history'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'lat': self.lat,
            'lng': self.lng,
            'speed': self.speed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
