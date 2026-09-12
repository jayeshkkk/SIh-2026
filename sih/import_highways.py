"""Import referenced national and state highways from OpenStreetMap.

The project stores district-to-district road segments, so OSM way endpoints
are mapped to the nearest seeded districts. Run this script after seeding:

    py import_highways.py

The importer only imports OSM ways with NH/SH references inside the NER
bounding box and is safe to run repeatedly.
"""
import math
import re
from datetime import datetime

import requests

from app import app
from models import db, District, RoadSegment

OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)
NER_BBOX = (21.5, 87.5, 29.8, 97.5)
REQUEST_HEADERS = {
    "User-Agent": "NER-LAIP-highway-importer/1.0 (local logistics dashboard)"
}
HIGHWAY_QUERY = """
[out:json][timeout:180];
way["highway"]["ref"~"^(NH|SH)[ -]", i](21.5,87.5,29.8,97.5);
out tags geom;
"""


def distance_km(lat1, lng1, lat2, lng2):
    return math.hypot((lat2 - lat1) * 111, (lng2 - lng1) * 102)


def nearest_district(point, districts):
    return min(
        districts,
        key=lambda district: distance_km(point["lat"], point["lon"], district.lat, district.lng)
    )


def highway_type(reference):
    return "national_highway" if re.search(r"\bNH\b", reference, re.I) else "state_highway"


def highway_number(reference):
    match = re.search(r"(?:NH|SH)[ -]*([A-Z0-9-]+)", reference, re.I)
    return match.group(1) if match else reference.upper()


def import_highways():
    response = None
    last_error = None
    for endpoint in OVERPASS_URLS:
        try:
            candidate = requests.post(
                endpoint,
                data=HIGHWAY_QUERY,
                headers=REQUEST_HEADERS,
                timeout=240
            )
            candidate.raise_for_status()
            response = candidate
            break
        except requests.RequestException as error:
            last_error = error

    if response is None:
        raise RuntimeError(f"All Overpass endpoints failed: {last_error}")

    elements = response.json().get("elements", [])

    districts = District.query.all()
    imported = 0
    skipped = 0

    for element in elements:
        geometry = element.get("geometry", [])
        tags = element.get("tags", {})
        if len(geometry) < 2 or not tags.get("ref"):
            skipped += 1
            continue

        start = nearest_district(geometry[0], districts)
        end = nearest_district(geometry[-1], districts)
        if start.id == end.id:
            skipped += 1
            continue

        reference = tags["ref"].strip().upper()
        road_name = tags.get("name") or f"{reference} {start.name}-{end.name}"
        existing = RoadSegment.query.filter(
            RoadSegment.name == road_name,
            RoadSegment.from_location == start.name,
            RoadSegment.to_location == end.name
        ).first()
        reverse_existing = RoadSegment.query.filter(
            RoadSegment.name == road_name,
            RoadSegment.from_location == end.name,
            RoadSegment.to_location == start.name
        ).first()
        if existing or reverse_existing:
            skipped += 1
            continue

        length_km = sum(
            distance_km(first["lat"], first["lon"], second["lat"], second["lon"])
            for first, second in zip(geometry, geometry[1:])
        )
        if length_km <= 0:
            skipped += 1
            continue

        road = RoadSegment(
            name=road_name,
            from_location=start.name,
            to_location=end.name,
            from_lat=geometry[0]["lat"],
            from_lng=geometry[0]["lon"],
            to_lat=geometry[-1]["lat"],
            to_lng=geometry[-1]["lon"],
            road_type=highway_type(reference),
            length_km=round(length_km, 1),
            status="open",
            condition="good",
            terrain_type="hilly",
            risk_score=0.3,
            last_inspection=datetime.utcnow(),
            weather_impact="none",
            traffic_level="normal",
            district_id=start.id
        )
        db.session.add(road)
        imported += 1

    db.session.commit()
    return imported, skipped


if __name__ == "__main__":
    with app.app_context():
        imported_count, skipped_count = import_highways()
        print(f"Imported {imported_count} highway segments; skipped {skipped_count} existing or unusable ways.")
