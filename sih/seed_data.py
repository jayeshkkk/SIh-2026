"""
NER Logistics Accessibility Intelligence Platform - Seed Data
Populates realistic data for North Eastern Region districts, roads, bridges, vehicles, etc.
"""
from datetime import datetime, timedelta
from models import db, District, RoadSegment, Bridge, Vehicle, FieldReport, Alert, WeatherData
import random
import json


def seed_all_data():
    """Seed all initial data for the platform."""
    seed_districts()
    seed_roads()
    seed_bridges()
    seed_vehicles()
    seed_field_reports()
    seed_alerts()
    seed_weather()


def seed_districts():
    """Seed North Eastern Region districts with real coordinates."""
    districts = [
        # Assam
        ('Guwahati', 'Assam', 26.1445, 91.7362, 957000, 'normal', 45, 28),
        ('Dibrugarh', 'Assam', 27.4728, 94.9120, 154000, 'normal', 32, 18),
        ('Jorhat', 'Assam', 26.7509, 94.2037, 155000, 'normal', 28, 15),
        ('Silchar', 'Assam', 24.8333, 92.7789, 172000, 'normal', 25, 12),
        ('Tezpur', 'Assam', 26.6339, 92.8000, 102000, 'warning', 22, 14),
        ('Nagaon', 'Assam', 26.3504, 92.6760, 147000, 'normal', 30, 16),
        ('Dhubri', 'Assam', 26.0207, 89.9743, 95000, 'normal', 18, 10),
        ('Goalpara', 'Assam', 26.1800, 90.6200, 78000, 'normal', 20, 11),
        ('Lakhimpur', 'Assam', 27.2363, 94.0958, 105000, 'normal', 24, 13),
        ('Karimganj', 'Assam', 24.8700, 92.3500, 72000, 'normal', 16, 9),
        # Arunachal Pradesh
        ('Itanagar', 'Arunachal Pradesh', 27.0844, 93.6053, 60000, 'warning', 20, 15),
        ('Pasighat', 'Arunachal Pradesh', 28.0667, 95.3333, 35000, 'normal', 14, 8),
        ('Bomdila', 'Arunachal Pradesh', 27.2667, 92.4167, 12000, 'critical', 10, 6),
        ('Tawang', 'Arunachal Pradesh', 27.5833, 91.8667, 11000, 'warning', 8, 5),
        ('Ziro', 'Arunachal Pradesh', 27.5500, 93.8333, 18000, 'normal', 12, 7),
        # Manipur
        ('Imphal', 'Manipur', 24.8170, 93.9368, 268000, 'normal', 35, 22),
        ('Churachandpur', 'Manipur', 24.3333, 93.6833, 48000, 'normal', 15, 9),
        ('Thoubal', 'Manipur', 24.6333, 94.0167, 46000, 'normal', 18, 11),
        # Meghalaya
        ('Shillong', 'Meghalaya', 25.5788, 91.8933, 143000, 'normal', 30, 20),
        ('Tura', 'Meghalaya', 25.5167, 90.2167, 75000, 'normal', 18, 10),
        ('Jowai', 'Meghalaya', 25.4500, 92.2000, 32000, 'warning', 12, 7),
        # Mizoram
        ('Aizawl', 'Mizoram', 23.7367, 92.7146, 293000, 'normal', 28, 18),
        ('Lunglei', 'Mizoram', 22.8833, 92.7333, 78000, 'normal', 16, 10),
        ('Champhai', 'Mizoram', 23.4667, 93.3333, 35000, 'normal', 12, 7),
        # Nagaland
        ('Kohima', 'Nagaland', 25.6747, 94.1100, 99000, 'normal', 22, 14),
        ('Dimapur', 'Nagaland', 25.9091, 93.7266, 122000, 'normal', 28, 16),
        ('Mokokchung', 'Nagaland', 26.3250, 94.5350, 36000, 'normal', 15, 9),
        # Sikkim
        ('Gangtok', 'Sikkim', 27.3314, 88.6138, 100000, 'warning', 20, 14),
        ('Namchi', 'Sikkim', 27.1667, 88.3667, 28000, 'normal', 12, 8),
        ('Gyalshing', 'Sikkim', 27.3000, 88.2500, 15000, 'critical', 8, 5),
        # Tripura
        ('Agartala', 'Tripura', 23.8315, 91.2868, 400000, 'normal', 38, 24),
        ('Udaipur', 'Tripura', 23.5333, 91.4833, 32000, 'normal', 14, 8),
        ('Dharmanagar', 'Tripura', 24.3667, 92.1667, 40000, 'normal', 16, 10),
    ]

    for d in districts:
        district = District(
            name=d[0], state=d[1], lat=d[2], lng=d[3],
            population=d[4], connectivity_status=d[5],
            road_count=d[6], bridge_count=d[7],
            last_updated=datetime.utcnow() - timedelta(hours=random.randint(0, 24))
        )
        db.session.add(district)
    db.session.commit()
    print(f"Seeded {len(districts)} districts.")


def seed_roads():
    """Seed major road segments connecting NER districts."""
    roads = [
        # NH-27 corridor
        ('NH-27 Guwahati-Dhubri', 'Guwahati', 'Dhubri', 26.1445, 91.7362, 26.0207, 89.9743, 'national_highway', 210.0, 'open', 'good', 'plains', 0.3, 'none', 'normal', 1),
        ('NH-27 Dhubri-Goalpara', 'Dhubri', 'Goalpara', 26.0207, 89.9743, 26.1800, 90.6200, 'national_highway', 95.0, 'open', 'fair', 'plains', 0.4, 'none', 'moderate', 1),
        ('NH-15 Guwahati-Tezpur', 'Guwahati', 'Tezpur', 26.1445, 91.7362, 26.6339, 92.8000, 'national_highway', 180.0, 'partial', 'fair', 'hilly', 0.6, 'road_damage', 'heavy', 1),
        ('NH-15 Tezpur-Bomdila', 'Tezpur', 'Bomdila', 26.6339, 92.8000, 27.2667, 92.4167, 'national_highway', 155.0, 'blocked', 'poor', 'mountainous', 0.85, 'landslide', 'none', 2),
        ('NH-229 Bomdila-Tawang', 'Bomdila', 'Tawang', 27.2667, 92.4167, 27.5833, 91.8667, 'national_highway', 170.0, 'partial', 'poor', 'mountainous', 0.9, 'snow', 'light', 2),
        # NH-37 corridor
        ('NH-37 Guwahati-Jorhat', 'Guwahati', 'Jorhat', 26.1445, 91.7362, 26.7509, 94.2037, 'national_highway', 315.0, 'open', 'good', 'plains', 0.25, 'none', 'moderate', 1),
        ('NH-37 Jorhat-Dibrugarh', 'Jorhat', 'Dibrugarh', 26.7509, 94.2037, 27.4728, 94.9120, 'national_highway', 145.0, 'open', 'good', 'plains', 0.3, 'none', 'normal', 1),
        ('NH-52 Jorhat-Pasighat', 'Jorhat', 'Pasighat', 26.7509, 94.2037, 28.0667, 95.3333, 'state_highway', 220.0, 'partial', 'fair', 'hilly', 0.7, 'flood', 'light', 2),
        # NH-6 corridor
        ('NH-6 Guwahati-Shillong', 'Guwahati', 'Shillong', 26.1445, 91.7362, 25.5788, 91.8933, 'national_highway', 100.0, 'open', 'good', 'hilly', 0.5, 'none', 'heavy', 3),
        ('NH-6 Shillong-Tura', 'Shillong', 'Tura', 25.5788, 91.8933, 25.5167, 90.2167, 'national_highway', 320.0, 'open', 'fair', 'hilly', 0.55, 'none', 'moderate', 3),
        ('NH-106 Shillong-Jowai', 'Shillong', 'Jowai', 25.5788, 91.8933, 25.4500, 92.2000, 'state_highway', 65.0, 'blocked', 'poor', 'hilly', 0.75, 'landslide', 'none', 3),
        # Manipur corridor
        ('NH-2 Imphal-Kohima', 'Imphal', 'Kohima', 24.8170, 93.9368, 25.6747, 94.1100, 'national_highway', 140.0, 'open', 'fair', 'hilly', 0.6, 'none', 'moderate', 5),
        ('NH-2 Kohima-Dimapur', 'Kohima', 'Dimapur', 25.6747, 94.1100, 25.9091, 93.7266, 'national_highway', 75.0, 'open', 'good', 'hilly', 0.4, 'none', 'heavy', 6),
        ('NH-37 Imphal-Silchar', 'Imphal', 'Silchar', 24.8170, 93.9368, 24.8333, 92.7789, 'national_highway', 260.0, 'partial', 'fair', 'hilly', 0.65, 'flood', 'moderate', 5),
        ('NH-102B Churachandpur-Aizawl', 'Churachandpur', 'Aizawl', 24.3333, 93.6833, 23.7367, 92.7146, 'national_highway', 190.0, 'open', 'fair', 'hilly', 0.55, 'none', 'moderate', 5),
        # Mizoram corridor
        ('NH-6 Silchar-Aizawl', 'Silchar', 'Aizawl', 24.8333, 92.7789, 23.7367, 92.7146, 'national_highway', 180.0, 'open', 'fair', 'mountainous', 0.7, 'none', 'moderate', 4),
        ('NH-54 Aizawl-Lunglei', 'Aizawl', 'Lunglei', 23.7367, 92.7146, 22.8833, 92.7333, 'state_highway', 165.0, 'open', 'fair', 'mountainous', 0.6, 'none', 'light', 7),
        # Nagaland corridor
        ('NH-29 Dimapur-Kohima', 'Dimapur', 'Kohima', 25.9091, 93.7266, 25.6747, 94.1100, 'national_highway', 75.0, 'open', 'good', 'hilly', 0.4, 'none', 'heavy', 6),
        ('NH-61 Mokokchung-Ziro', 'Mokokchung', 'Ziro', 26.3250, 94.5350, 27.5500, 93.8333, 'state_highway', 110.0, 'partial', 'poor', 'mountainous', 0.8, 'landslide', 'light', 8),
        # Sikkim corridor
        ('NH-10 Siliguri-Gangtok', 'Siliguri', 'Gangtok', 26.7271, 88.3953, 27.3314, 88.6138, 'national_highway', 115.0, 'partial', 'fair', 'mountainous', 0.75, 'landslide', 'heavy', 10),
        ('NH-510 Gangtok-Namchi', 'Gangtok', 'Namchi', 27.3314, 88.6138, 27.1667, 88.3667, 'state_highway', 80.0, 'open', 'fair', 'hilly', 0.55, 'none', 'moderate', 10),
        ('NH-710 Gyalshing-Namchi', 'Gyalshing', 'Namchi', 27.3000, 88.2500, 27.1667, 88.3667, 'state_highway', 50.0, 'blocked', 'poor', 'mountainous', 0.85, 'road_damage', 'none', 10),
        # Tripura corridor
        ('NH-8 Agartala-Udaipur', 'Agartala', 'Udaipur', 23.8315, 91.2868, 23.5333, 91.4833, 'national_highway', 55.0, 'open', 'good', 'plains', 0.2, 'none', 'moderate', 11),
        ('NH-8A Agartala-Dharmanagar', 'Agartala', 'Dharmanagar', 23.8315, 91.2868, 24.3667, 92.1667, 'national_highway', 195.0, 'open', 'good', 'plains', 0.25, 'none', 'normal', 11),
        ('NH-44 Agartala-Silchar', 'Agartala', 'Silchar', 23.8315, 91.2868, 24.8333, 92.7789, 'national_highway', 260.0, 'partial', 'fair', 'hilly', 0.5, 'flood', 'moderate', 4),
        # Assam internal
        ('SH-1 Guwahati-Nagaon', 'Guwahati', 'Nagaon', 26.1445, 91.7362, 26.3504, 92.6760, 'state_highway', 125.0, 'open', 'good', 'plains', 0.3, 'none', 'heavy', 1),
        ('SH-2 Nagaon-Karimganj', 'Nagaon', 'Karimganj', 26.3504, 92.6760, 24.8700, 92.3500, 'state_highway', 280.0, 'partial', 'fair', 'plains', 0.5, 'flood', 'moderate', 1),
        ('SH-11 Lakhimpur-Itanagar', 'Lakhimpur', 'Itanagar', 27.2363, 94.0958, 27.0844, 93.6053, 'state_highway', 90.0, 'partial', 'fair', 'hilly', 0.7, 'landslide', 'light', 2),
        # Mizoram-Nagaland link
        ('MR Champhai-Mokokchung', 'Champhai', 'Mokokchung', 23.4667, 93.3333, 26.3250, 94.5350, 'district_road', 240.0, 'open', 'poor', 'mountainous', 0.8, 'none', 'light', 8),
    ]

    for r in roads:
        now = datetime.utcnow()
        block_since = now - timedelta(hours=random.randint(2, 48)) if r[11] == 'blocked' else None
        estimated_reopen = block_since + timedelta(hours=random.randint(12, 72)) if block_since else None

        road = RoadSegment(
            name=r[0], from_location=r[1], to_location=r[2],
            from_lat=r[3], from_lng=r[4], to_lat=r[5], to_lng=r[6],
            road_type=r[7], length_km=r[8], status=r[9], condition=r[10],
            terrain_type=r[11], risk_score=r[12],
            last_inspection=now - timedelta(days=random.randint(1, 30)),
            block_reason=r[13] if r[9] == 'blocked' else None,
            block_since=block_since,
            estimated_reopen=estimated_reopen,
            weather_impact=r[13] if r[13] != 'none' else 'none',
            traffic_level=r[14],
            district_id=r[15]
        )
        db.session.add(road)
    db.session.commit()
    print(f"Seeded {len(roads)} road segments.")


def seed_bridges():
    """Seed bridge data across NER."""
    bridges = [
        ('Brahmaputra Bridge - Guwahati', 26.1445, 91.7362, 2500.0, 'operational', 'good', 40.0, 1962, 'Brahmaputra', 0.2, 1),
        ('Kalia Bhomora Setu', 26.7000, 92.8000, 3015.0, 'operational', 'good', 35.0, 1987, 'Brahmaputra', 0.3, 1),
        ('Saraighat Bridge', 26.1000, 91.7000, 1497.0, 'operational', 'fair', 30.0, 1962, 'Brahmaputra', 0.35, 1),
        ('Bogibeel Bridge', 27.4000, 94.9000, 4748.0, 'operational', 'good', 50.0, 2018, 'Brahmaputra', 0.15, 1),
        ('Naranarayan Setu', 26.1000, 90.6000, 2300.0, 'operational', 'good', 40.0, 1998, 'Brahmaputra', 0.25, 1),
        ('Kolia Bhomora Bridge - Tezpur', 26.6339, 92.8000, 3015.0, 'partial', 'fair', 35.0, 1987, 'Brahmaputra', 0.55, 1),
        ('Siang River Bridge', 28.0667, 95.3333, 850.0, 'operational', 'fair', 25.0, 2005, 'Siang', 0.4, 2),
        ('Subansiri Bridge - Ziro', 27.5500, 93.8333, 650.0, 'operational', 'poor', 15.0, 1995, 'Subansiri', 0.6, 2),
        ('Kameng River Bridge', 27.2667, 92.4167, 480.0, 'partial', 'poor', 12.0, 1990, 'Kameng', 0.8, 2),
        ('Barak River Bridge - Silchar', 24.8333, 92.7789, 720.0, 'operational', 'fair', 20.0, 2002, 'Barak', 0.45, 4),
        ('Umngot River Bridge', 25.5788, 91.8933, 350.0, 'operational', 'good', 18.0, 2010, 'Umngot', 0.3, 3),
        ('Kynshi River Bridge', 25.5167, 90.2167, 420.0, 'operational', 'fair', 15.0, 2008, 'Kynshi', 0.4, 3),
        ('Tlawng River Bridge', 23.7367, 92.7146, 380.0, 'operational', 'good', 20.0, 2012, 'Tlawng', 0.25, 7),
        ('Tuivai River Bridge', 22.8833, 92.7333, 290.0, 'operational', 'fair', 12.0, 2005, 'Tuivai', 0.35, 7),
        ('Doyang River Bridge', 25.6747, 94.1100, 550.0, 'operational', 'fair', 18.0, 2003, 'Doyang', 0.3, 6),
        ('Dhansiri River Bridge', 25.9091, 93.7266, 620.0, 'operational', 'good', 22.0, 2007, 'Dhansiri', 0.25, 6),
        ('Teesta River Bridge - Gangtok', 27.3314, 88.6138, 480.0, 'partial', 'fair', 15.0, 1998, 'Teesta', 0.7, 10),
        ('Rangeet River Bridge', 27.1667, 88.3667, 350.0, 'operational', 'fair', 14.0, 2004, 'Rangeet', 0.45, 10),
        ('Gumti River Bridge', 23.8315, 91.2868, 580.0, 'operational', 'good', 20.0, 2006, 'Gumti', 0.2, 11),
        ('Manas River Bridge', 26.3504, 92.6760, 750.0, 'operational', 'fair', 22.0, 2001, 'Manas', 0.35, 1),
    ]

    for b in bridges:
        bridge = Bridge(
            name=b[0], lat=b[1], lng=b[2], length_m=b[3],
            status=b[4], condition=b[5], load_capacity_tons=b[6],
            built_year=b[7],
            last_inspection=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            river_name=b[8], risk_score=b[9], district_id=b[10]
        )
        db.session.add(bridge)
    db.session.commit()
    print(f"Seeded {len(bridges)} bridges.")


def seed_vehicles():
    """Seed vehicle tracking data."""
    vehicles = [
        ('AS-01-G-1234', 'truck', 'medicine', 'COVID-19 Vaccines (5000 doses)', 2000.0, 26.2000, 91.7500, 'active', 45.0, 45.0, 'Rajesh Das', '+91-9876543210', 'Guwahati', 'Dibrugarh', None, 1),
        ('AS-01-H-5678', 'truck', 'food', 'Rice and Wheat (1000 bags)', 5000.0, 26.5000, 92.0000, 'active', 35.0, 60.0, 'Manoj Sharma', '+91-9876543211', 'Guwahati', 'Tezpur', None, 1),
        ('AR-02-B-9012', 'van', 'medicine', 'Emergency Medical Supplies', 800.0, 27.2000, 93.5000, 'delayed', 0.0, 0.0, 'Tenzin Dorjee', '+91-9876543212', 'Itanagar', 'Tawang', None, 2),
        ('ML-03-C-3456', 'truck', 'construction', 'Cement and Steel', 8000.0, 24.8500, 93.9000, 'active', 30.0, 120.0, 'Thoiba Singh', '+91-9876543213', 'Imphal', 'Churachandpur', None, 5),
        ('MZ-04-D-7890', 'truck', 'agriculture', 'Fresh Vegetables', 3000.0, 23.7500, 92.7000, 'active', 40.0, 90.0, 'Lalruata', '+91-9876543214', 'Aizawl', 'Lunglei', None, 7),
        ('NL-05-E-1122', 'van', 'medicine', 'Essential Drugs', 1200.0, 25.7000, 94.0000, 'active', 50.0, 180.0, 'Neichute', '+91-9876543215', 'Kohima', 'Mokokchung', None, 6),
        ('SK-06-F-3344', 'truck', 'food', 'Relief Supplies', 4000.0, 27.3000, 88.6000, 'delayed', 15.0, 270.0, 'Dorjee Lama', '+91-9876543216', 'Gangtok', 'Namchi', None, 10),
        ('TR-07-G-5566', 'truck', 'construction', 'Building Materials', 6000.0, 23.8500, 91.3000, 'active', 38.0, 15.0, 'Biplab Deb', '+91-9876543217', 'Agartala', 'Udaipur', None, 11),
        ('AS-01-J-7788', 'tanker', 'fuel', 'Diesel (5000L)', 4500.0, 26.4000, 91.5000, 'active', 42.0, 75.0, 'Pranjal Bora', '+91-9876543218', 'Guwahati', 'Jorhat', None, 1),
        ('ML-03-K-9900', 'truck', 'agriculture', 'Potatoes and Ginger', 3500.0, 24.7500, 94.0000, 'active', 28.0, 210.0, 'Sanatomba', '+91-9876543219', 'Imphal', 'Kohima', None, 5),
        ('AR-02-L-2233', 'van', 'medicine', 'Oxygen Cylinders', 600.0, 27.4500, 93.8000, 'active', 35.0, 30.0, 'Nabam Tuki', '+91-9876543220', 'Pasighat', 'Itanagar', None, 2),
        ('MZ-04-M-4455', 'truck', 'food', 'Ration Supplies', 4500.0, 22.9000, 92.7500, 'delayed', 0.0, 0.0, 'R Lalhruaia', '+91-9876543221', 'Lunglei', 'Aizawl', None, 7),
        ('NL-05-N-6677', 'truck', 'construction', 'Road Repair Materials', 7000.0, 25.8500, 93.7000, 'active', 32.0, 135.0, 'K Temjen', '+91-9876543222', 'Dimapur', 'Kohima', None, 6),
        ('SK-06-P-8899', 'van', 'medicine', 'Vaccines and Insulin', 500.0, 27.2000, 88.4000, 'active', 25.0, 315.0, 'Sonam Gyatso', '+91-9876543223', 'Namchi', 'Gyalshing', None, 10),
        ('TR-07-Q-0011', 'truck', 'agriculture', 'Jute and Tea', 4000.0, 24.3000, 92.1000, 'active', 45.0, 50.0, 'Manik Saha', '+91-9876543224', 'Dharmanagar', 'Agartala', None, 11),
    ]

    now = datetime.utcnow()
    for v in vehicles:
        eta = now + timedelta(hours=random.randint(2, 24)) if v[7] != 'delayed' else now + timedelta(hours=random.randint(6, 48))
        vehicle = Vehicle(
            vehicle_number=v[0], vehicle_type=v[1], cargo_type=v[2],
            cargo_description=v[3], capacity_kg=v[4],
            current_lat=v[5], current_lng=v[6], status=v[7],
            speed_kmh=v[8], heading=v[9], driver_name=v[10],
            driver_phone=v[11], origin=v[12], destination=v[13],
            eta=eta, last_update=now - timedelta(minutes=random.randint(1, 30)),
            district_id=v[15]
        )
        db.session.add(vehicle)
    db.session.commit()
    print(f"Seeded {len(vehicles)} vehicles.")


def seed_field_reports():
    """Seed field reports from remote locations."""
    reports = [
        ('road_block', 'Landslide on NH-15 near Bomdila', 'Large boulders blocking both lanes, approximately 200m stretch affected. Debris removal underway.', 27.2500, 92.4200, 'NH-15, km 145, Bomdila', None, 'critical', 'in_progress', 'Tenzing Bhutia', '+91-9876500001', 'PWD Engineer', 2),
        ('road_damage', 'Bridge approach washed out near Tezpur', 'Heavy rainfall caused erosion of approach road to Kolia Bhomora Bridge. Single lane traffic only.', 26.6300, 92.7900, 'Kolia Bhomora Bridge approach, Tezpur', None, 'high', 'verified', 'Ramesh Kalita', '+91-9876500002', 'SDO PWD', 1),
        ('flood', 'Barak River flooding near Silchar', 'Water level rising rapidly. Low-lying areas inundated. Road connecting Silchar to Mizoram affected.', 24.8200, 92.7600, 'Barak River, Silchar', None, 'critical', 'verified', 'Anil Das', '+91-9876500003', 'District Emergency Officer', 4),
        ('landslide', 'Landslide at Sela Pass', 'Massive landslide triggered by continuous rain. Road completely blocked. Army BRO teams deployed.', 27.5000, 92.1000, 'Sela Pass, Tawang District', None, 'critical', 'in_progress', 'Major R Singh', '+91-9876500004', 'BRO Officer', 2),
        ('traffic_congestion', 'Heavy traffic jam at Jorhat junction', 'Two-hour delay due to festival traffic and ongoing road repair work. Diversions in place.', 26.7450, 94.1950, 'Jorhat Main Road Junction', None, 'medium', 'resolved', 'Bikash Gogoi', '+91-9876500005', 'Traffic Police', 1),
        ('road_damage', 'Potholes and cracks on NH-6 Shillong-Tura', 'Multiple sections with severe potholes causing vehicle damage. Repair urgently needed.', 25.5500, 91.0500, 'NH-6, km 85-92, West Khasi Hills', None, 'high', 'pending', 'Sanborlang', '+91-9876500006', 'PWD Supervisor', 3),
        ('flood', 'Flash flood near Agartala-Dharmanagar road', 'Sudden water logging on NH-8A. Depth 2-3 feet in some sections. Traffic diverted.', 24.1000, 91.8000, 'NH-8A, Kumarghat area', None, 'high', 'in_progress', 'Ratan Dey', '+91-9876500007', 'PWD AE', 11),
        ('landslide', 'Minor landslide on Gangtok-Namchi road', 'Soil slip blocking one lane. JCB deployed for clearance. Expected to clear in 4 hours.', 27.2200, 88.5000, 'NH-510, near Temi Tea Garden', None, 'medium', 'in_progress', 'Pema Sherpa', '+91-9876500008', 'NH Division Engineer', 10),
        ('road_block', 'Tree fall blocking road to remote village', 'Large tree uprooted and blocking village road connecting to NH-2. Local community clearing.', 25.5000, 94.0000, 'Village road, Peren District', None, 'medium', 'pending', 'Kevi Vizo', '+91-9876500009', 'Circle Officer', 6),
        ('bridge_issue', 'Bridge vibration warning - Aizawl-Lunglei', 'Vibrations felt on bridge deck during vehicle crossing. Structural inspection recommended.', 23.1000, 92.7200, 'Bridge No. 4, Aizawl-Lunglei Road', None, 'high', 'verified', 'Lalthlamuana', '+91-9876500010', 'PWD Executive Engineer', 7),
        ('road_damage', 'Severe cracking on NH-37 Jorhat-Dibrugarh', 'Thermal cracking and edge damage over 5km stretch. Speed restriction imposed.', 26.9500, 94.4000, 'NH-37, km 45-50, Sivasagar District', None, 'medium', 'in_progress', 'Hemanta Borah', '+91-9876500011', 'NHAI PIU', 1),
        ('flood', 'River overflow near Imphal-Silchar road', 'Iril River overflowing at multiple points. Water on road surface. Caution advised.', 24.9000, 93.5000, 'NH-37, near Jiribam', None, 'high', 'verified', 'Thoiba Singh', '+91-9876500012', 'SDO PWD', 5),
        ('landslide', 'Landslide debris on NH-10 near Rangpo', 'Fresh landslide blocking half of road. BRO on standby. No vehicle damage reported.', 27.1800, 88.5500, 'NH-10, Rangpo Check Post', None, 'medium', 'in_progress', 'Tshering Bhutia', '+91-9876500013', 'BRO JCO', 10),
    ]

    for r in reports:
        report = FieldReport(
            report_type=r[0], title=r[1], description=r[2],
            lat=r[3], lng=r[4], location_name=r[5],
            photo_url=r[6], severity=r[7], status=r[8],
            reported_by=r[9], reporter_phone=r[10],
            reporter_designation=r[11],
            reported_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            verified=(r[8] == 'verified' or r[8] == 'resolved'),
            verified_by='District Admin' if r[8] in ['verified', 'resolved'] else None,
            verified_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)) if r[8] in ['verified', 'resolved'] else None,
            district_id=r[12]
        )
        db.session.add(report)
    db.session.commit()
    print(f"Seeded {len(reports)} field reports.")


def seed_alerts():
    """Seed system alerts."""
    alerts = [
        ('landslide', 'LANDSLIDE WARNING: Sela Pass Area', 'Continuous rainfall has increased landslide risk on Sela Pass (NH-229). BRO advises avoiding travel after 6 PM. Carry snow chains if essential.', 'critical', 27.5000, 92.1000, 'Sela Pass, Tawang District', 'Tawang, Bomdila', 'active', datetime.utcnow() + timedelta(days=3), 'IMD + BRO'),
        ('flood', 'FLOOD ALERT: Barak River Basin', 'Barak River water level crossed danger mark at Silchar. NH-37 and connecting roads may be submerged. Evacuation advisories issued for low-lying areas.', 'critical', 24.8200, 92.7600, 'Barak River, Cachar District', 'Silchar, Karimganj, Hailakandi', 'active', datetime.utcnow() + timedelta(days=2), 'CWC + District Admin'),
        ('road_block', 'ROAD CLOSURE: NH-15 Bomdila-Tawang', 'Multiple landslides and snow accumulation have rendered NH-15 impassable between Bomdila and Tawang. BRO clearance operations ongoing. Estimated reopening: 48 hours.', 'critical', 27.2667, 92.4167, 'NH-15, West Kameng District', 'Bomdila, Tawang, Dirang', 'active', datetime.utcnow() + timedelta(days=2), 'BRO + PWD'),
        ('weather', 'HEAVY RAINFALL WARNING: Assam & Meghalaya', 'IMD predicts heavy to very heavy rainfall (150-200mm) in Assam and Meghalaya over next 48 hours. Flash flood and landslide risk HIGH.', 'high', 26.1445, 91.7362, 'Assam & Meghalaya Region', 'All Assam districts, East & West Khasi Hills', 'active', datetime.utcnow() + timedelta(hours=48), 'IMD Guwahati'),
        ('traffic', 'TRAFFIC CONGESTION: Guwahati City', 'Festival season causing severe traffic congestion in Guwahati. Average speed dropped to 15 km/h. Use alternate routes via NH-27 bypass.', 'medium', 26.1445, 91.7362, 'Guwahati Metropolitan Area', 'Kamrup Metropolitan', 'active', datetime.utcnow() + timedelta(hours=12), 'Traffic Police'),
        ('road_block', 'BRIDGE CLOSURE: Gyalshing-Namchi', 'Bridge No. 3 on NH-710 near Gyalshing declared unsafe after inspection. Complete closure until repairs completed.', 'high', 27.3000, 88.2500, 'NH-710, West Sikkim', 'Gyalshing, Namchi', 'active', datetime.utcnow() + timedelta(days=7), 'PWD Sikkim'),
        ('weather', 'THUNDERSTORM WARNING: Tripura & Mizoram', 'Severe thunderstorm with gusty winds (60-70 km/h) expected in Tripura and Mizoram. Temporary road closures possible due to tree falls.', 'medium', 23.8315, 91.2868, 'Tripura & Mizoram Region', 'All districts', 'active', datetime.utcnow() + timedelta(hours=24), 'IMD Agartala'),
        ('delivery_delay', 'SUPPLY DELAY: Medicine shipment to Tawang', 'Medicine truck (AR-02-B-9012) delayed at Bomdila due to road block. Emergency airlift being arranged for critical supplies.', 'high', 27.2667, 92.4167, 'Bomdila Check Post', 'Tawang District', 'active', datetime.utcnow() + timedelta(days=1), 'Health Dept + Transport'),
        ('landslide', 'LANDSLIDE ALERT: NH-510 Gangtok-Namchi', 'Landslide-prone area active between km 12-18. Single lane operation. Night travel prohibited.', 'medium', 27.2200, 88.5000, 'NH-510, South Sikkim', 'Gangtok, Namchi', 'active', datetime.utcnow() + timedelta(days=5), 'NH Division Sikkim'),
        ('flood', 'RIVER LEVEL RISING: Siang Basin', 'Siang River water level rising rapidly. Alert issued for downstream areas. NH-52 at risk of submergence.', 'high', 28.0667, 95.3333, 'Siang River, East Siang District', 'Pasighat, East Siang', 'active', datetime.utcnow() + timedelta(hours=36), 'CWC Dibrugarh'),
    ]

    for a in alerts:
        alert = Alert(
            alert_type=a[0], title=a[1], message=a[2],
            severity=a[3], lat=a[4], lng=a[5],
            location_name=a[6], affected_districts=a[7],
            status=a[8], created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 12)),
            expires_at=a[9], source=a[10]
        )
        db.session.add(alert)
    db.session.commit()
    print(f"Seeded {len(alerts)} alerts.")


def seed_weather():
    """Seed weather data for NER districts."""
    weather_conditions = [
        # Assam
        (1, 'Guwahati', 26.1445, 91.7362, 31.0, 78.0, 12.5, 15.0, 8.0, 'heavy_rain', 'high', 'medium'),
        (1, 'Dibrugarh', 27.4728, 94.9120, 29.0, 82.0, 45.0, 20.0, 4.0, 'torrential', 'critical', 'high'),
        (1, 'Jorhat', 26.7509, 94.2037, 30.0, 80.0, 25.0, 18.0, 6.0, 'heavy_rain', 'high', 'medium'),
        (1, 'Silchar', 24.8333, 92.7789, 28.0, 88.0, 120.0, 25.0, 2.0, 'torrential', 'critical', 'high'),
        (1, 'Tezpur', 26.6339, 92.8000, 30.5, 75.0, 35.0, 22.0, 5.0, 'heavy_rain', 'high', 'medium'),
        # Arunachal
        (2, 'Itanagar', 27.0844, 93.6053, 26.0, 85.0, 55.0, 10.0, 3.0, 'heavy_rain', 'high', 'high'),
        (2, 'Bomdila', 27.2667, 92.4167, 18.0, 92.0, 80.0, 8.0, 1.5, 'torrential', 'critical', 'critical'),
        (2, 'Tawang', 27.5833, 91.8667, 12.0, 95.0, 45.0, 25.0, 0.5, 'snow_rain', 'medium', 'critical'),
        # Manipur
        (5, 'Imphal', 24.8170, 93.9368, 29.0, 76.0, 15.0, 12.0, 9.0, 'moderate_rain', 'medium', 'low'),
        (5, 'Churachandpur', 24.3333, 93.6833, 27.0, 80.0, 20.0, 10.0, 7.0, 'moderate_rain', 'medium', 'medium'),
        # Meghalaya
        (3, 'Shillong', 25.5788, 91.8933, 22.0, 90.0, 65.0, 15.0, 3.0, 'torrential', 'critical', 'high'),
        (3, 'Tura', 25.5167, 90.2167, 26.0, 85.0, 40.0, 12.0, 5.0, 'heavy_rain', 'high', 'medium'),
        # Mizoram
        (7, 'Aizawl', 23.7367, 92.7146, 25.0, 78.0, 18.0, 14.0, 8.0, 'moderate_rain', 'medium', 'low'),
        (7, 'Lunglei', 22.8833, 92.7333, 24.0, 82.0, 22.0, 12.0, 7.0, 'moderate_rain', 'medium', 'medium'),
        # Nagaland
        (6, 'Kohima', 25.6747, 94.1100, 23.0, 80.0, 30.0, 10.0, 6.0, 'heavy_rain', 'high', 'high'),
        (6, 'Dimapur', 25.9091, 93.7266, 28.0, 75.0, 15.0, 8.0, 9.0, 'moderate_rain', 'medium', 'low'),
        # Sikkim
        (10, 'Gangtok', 27.3314, 88.6138, 20.0, 88.0, 50.0, 18.0, 2.0, 'heavy_rain', 'high', 'high'),
        (10, 'Gyalshing', 27.3000, 88.2500, 19.0, 90.0, 55.0, 15.0, 1.5, 'torrential', 'critical', 'critical'),
        # Tripura
        (11, 'Agartala', 23.8315, 91.2868, 30.0, 72.0, 8.0, 10.0, 10.0, 'light_rain', 'low', 'low'),
        (11, 'Dharmanagar', 24.3667, 92.1667, 29.0, 75.0, 12.0, 12.0, 8.0, 'moderate_rain', 'medium', 'low'),
    ]

    for w in weather_conditions:
        weather = WeatherData(
            district_id=w[0], location_name=w[1],
            lat=w[2], lng=w[3], temperature=w[4],
            humidity=w[5], rainfall_mm=w[6], wind_speed=w[7],
            visibility_km=w[8], weather_condition=w[9],
            flood_risk=w[10], landslide_risk=w[11],
            recorded_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 120)),
            forecast_24h=json.dumps({
                'morning': {'temp': w[4]-2, 'rain': w[6]*0.8, 'condition': w[9]},
                'afternoon': {'temp': w[4]+3, 'rain': w[6]*1.2, 'condition': w[9]},
                'evening': {'temp': w[4]-1, 'rain': w[6]*0.9, 'condition': 'cloudy'},
                'night': {'temp': w[4]-4, 'rain': w[6]*0.5, 'condition': 'cloudy'}
            })
        )
        db.session.add(weather)
    db.session.commit()
    print(f"Seeded {len(weather_conditions)} weather records.")
