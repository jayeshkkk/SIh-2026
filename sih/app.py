"""
NER Logistics Accessibility Intelligence Platform - Main Flask Application
AI-powered Smart Logistics & Accessibility Intelligence Platform for North Eastern Region (NER)
"""
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from models import db, District, RoadSegment, Bridge, Vehicle, FieldReport, Alert, WeatherData, RouteHistory
from seed_data import seed_all_data, seed_weather
from ai_engine import RoutePredictionEngine, DashboardAnalytics

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ner_logistics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ner-logistics-platform-secret-key-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
CORS(app)

ai_engine = RoutePredictionEngine()


# ==================== INITIALIZATION ====================

@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()


@app.route('/api/seed', methods=['POST'])
def seed_database():
    """Seed the database with initial NER data."""
    try:
        seed_all_data()
        return jsonify({'success': True, 'message': 'Database seeded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== MAIN PAGES ====================

@app.route('/')
def index():
    """Landing page / Home dashboard."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Keep the legacy dashboard URL pointed at the canonical dashboard."""
    return redirect('/')


@app.route('/map')
def map_view():
    """Interactive GIS map page."""
    return render_template('map.html')


@app.route('/vehicles')
def vehicles_page():
    """Vehicle tracking page."""
    return render_template('vehicles.html')


@app.route('/field-reports')
def field_reports_page():
    """Field reporting module page."""
    return render_template('field_reports.html')


@app.route('/route-planner')
def route_planner_page():
    """AI route planner page."""
    return render_template('route_planner.html')


@app.route('/predictions')
def predictions_page():
    """AI predictions page."""
    return render_template('predictions.html')


# ==================== API: DISTRICTS ====================

@app.route('/api/districts', methods=['GET'])
def get_districts():
    """Get all districts."""
    state = request.args.get('state')
    query = District.query
    if state:
        query = query.filter_by(state=state)
    districts = query.all()
    return jsonify([d.to_dict() for d in districts])


@app.route('/api/districts/<int:district_id>', methods=['GET'])
def get_district(district_id):
    """Get a specific district with its roads and bridges."""
    district = District.query.get_or_404(district_id)
    data = district.to_dict()
    data['roads'] = [r.to_dict() for r in RoadSegment.query.filter_by(district_id=district_id).all()]
    data['bridges'] = [b.to_dict() for b in Bridge.query.filter_by(district_id=district_id).all()]
    data['vehicles'] = [v.to_dict() for v in Vehicle.query.filter_by(district_id=district_id).all()]
    return jsonify(data)


# ==================== API: ROADS ====================

@app.route('/api/roads', methods=['GET'])
def get_roads():
    """Get all road segments with optional filters."""
    status = request.args.get('status')
    district_id = request.args.get('district_id', type=int)
    query = RoadSegment.query
    if status:
        query = query.filter_by(status=status)
    if district_id:
        query = query.filter_by(district_id=district_id)
    roads = query.all()
    return jsonify([r.to_dict() for r in roads])


@app.route('/api/roads/<int:road_id>', methods=['GET'])
def get_road(road_id):
    """Get a specific road segment."""
    road = RoadSegment.query.get_or_404(road_id)
    return jsonify(road.to_dict())


@app.route('/api/roads/<int:road_id>/status', methods=['PUT'])
def update_road_status(road_id):
    """Update road status."""
    road = RoadSegment.query.get_or_404(road_id)
    data = request.get_json()
    road.status = data.get('status', road.status)
    road.condition = data.get('condition', road.condition)
    road.block_reason = data.get('block_reason', road.block_reason)
    if road.status == 'blocked':
        road.block_since = datetime.utcnow()
    road.last_inspection = datetime.utcnow()
    db.session.commit()
    return jsonify(road.to_dict())


# ==================== API: BRIDGES ====================

@app.route('/api/bridges', methods=['GET'])
def get_bridges():
    """Get all bridges with optional filters."""
    status = request.args.get('status')
    district_id = request.args.get('district_id', type=int)
    query = Bridge.query
    if status:
        query = query.filter_by(status=status)
    if district_id:
        query = query.filter_by(district_id=district_id)
    bridges = query.all()
    return jsonify([b.to_dict() for b in bridges])


@app.route('/api/bridges/<int:bridge_id>', methods=['GET'])
def get_bridge(bridge_id):
    """Get a specific bridge."""
    bridge = Bridge.query.get_or_404(bridge_id)
    return jsonify(bridge.to_dict())


# ==================== API: VEHICLES / GPS TRACKING ====================

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicles with optional filters."""
    status = request.args.get('status')
    cargo_type = request.args.get('cargo_type')
    query = Vehicle.query
    if status:
        query = query.filter_by(status=status)
    if cargo_type:
        query = query.filter_by(cargo_type=cargo_type)
    vehicles = query.all()
    return jsonify([v.to_dict() for v in vehicles])


@app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Get a specific vehicle with route history."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = vehicle.to_dict()
    data['route_history'] = [r.to_dict() for r in RouteHistory.query.filter_by(vehicle_id=vehicle_id).order_by(RouteHistory.timestamp.desc()).limit(50).all()]
    return jsonify(data)


@app.route('/api/vehicles/<int:vehicle_id>/location', methods=['PUT'])
def update_vehicle_location(vehicle_id):
    """Update vehicle GPS location."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    vehicle.current_lat = data.get('lat', vehicle.current_lat)
    vehicle.current_lng = data.get('lng', vehicle.current_lng)
    vehicle.speed_kmh = data.get('speed_kmh', vehicle.speed_kmh)
    vehicle.heading = data.get('heading', vehicle.heading)
    vehicle.status = data.get('status', vehicle.status)
    vehicle.last_update = datetime.utcnow()

    # Add to route history
    if vehicle.current_lat and vehicle.current_lng:
        history = RouteHistory(
            vehicle_id=vehicle_id,
            lat=vehicle.current_lat,
            lng=vehicle.current_lng,
            speed=vehicle.speed_kmh
        )
        db.session.add(history)

    db.session.commit()
    return jsonify(vehicle.to_dict())


@app.route('/api/vehicles/<int:vehicle_id>/eta', methods=['GET'])
def get_vehicle_eta(vehicle_id):
    """Get AI-estimated arrival time for a vehicle."""
    eta_info = ai_engine.estimate_eta(vehicle_id)
    if eta_info:
        return jsonify(eta_info)
    return jsonify({'error': 'Vehicle not found'}), 404


# ==================== API: FIELD REPORTS ====================

@app.route('/api/field-reports', methods=['GET'])
def get_field_reports():
    """Get all field reports with optional filters."""
    report_type = request.args.get('report_type')
    status = request.args.get('status')
    district_id = request.args.get('district_id', type=int)
    query = FieldReport.query
    if report_type:
        query = query.filter_by(report_type=report_type)
    if status:
        query = query.filter_by(status=status)
    if district_id:
        query = query.filter_by(district_id=district_id)
    reports = query.order_by(FieldReport.reported_at.desc()).all()
    return jsonify([r.to_dict() for r in reports])


@app.route('/api/field-reports', methods=['POST'])
def create_field_report():
    """Create a new field report."""
    data = request.get_json()
    if not data or not data.get('photo_url'):
        return jsonify({'error': 'Image proof is required for field reports'}), 400

    report = FieldReport(
        report_type=data.get('report_type', 'other'),
        title=data.get('title', ''),
        description=data.get('description', ''),
        lat=data.get('lat', 0.0),
        lng=data.get('lng', 0.0),
        location_name=data.get('location_name', ''),
        photo_url=data.get('photo_url', ''),
        severity=data.get('severity', 'medium'),
        reported_by=data.get('reported_by', ''),
        reporter_phone=data.get('reporter_phone', ''),
        reporter_designation=data.get('reporter_designation', ''),
        district_id=data.get('district_id')
    )
    db.session.add(report)
    db.session.commit()

    # Auto-create alert for critical/high severity reports
    if report.severity in ['critical', 'high']:
        alert = Alert(
            alert_type=report.report_type,
            title=f"FIELD REPORT: {report.title}",
            message=report.description,
            severity=report.severity,
            lat=report.lat,
            lng=report.lng,
            location_name=report.location_name,
            source=f"Field Report - {report.reported_by}"
        )
        db.session.add(alert)
        db.session.commit()

    return jsonify(report.to_dict()), 201


@app.route('/api/field-reports/<int:report_id>/verify', methods=['PUT'])
def verify_field_report(report_id):
    """Verify a field report."""
    report = FieldReport.query.get_or_404(report_id)
    data = request.get_json()
    report.verified = True
    report.verified_by = data.get('verified_by', 'Admin')
    report.verified_at = datetime.utcnow()
    report.status = data.get('status', 'verified')
    db.session.commit()
    return jsonify(report.to_dict())


# ==================== API: WEATHER ====================

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data for all or specific district."""
    district_id = request.args.get('district_id', type=int)
    query = WeatherData.query
    if district_id:
        query = query.filter_by(district_id=district_id)
    weather = query.order_by(WeatherData.recorded_at.desc()).all()
    return jsonify([w.to_dict() for w in weather])


# ==================== API: AI / PREDICTIONS ====================

@app.route('/api/predictions/disruptions', methods=['GET'])
def get_disruption_predictions():
    """Get AI-predicted route disruptions."""
    hours_ahead = request.args.get('hours', 24, type=int)
    predictions = ai_engine.predict_disruptions(hours_ahead)
    return jsonify({
        'predictions': predictions,
        'generated_at': datetime.utcnow().isoformat(),
        'model_version': 'v1.0',
        'total_predicted': len(predictions)
    })


@app.route('/api/routes/alternate', methods=['GET'])
def get_alternate_routes():
    """Get AI-suggested alternate routes."""
    from_loc = request.args.get('from')
    to_loc = request.args.get('to')
    avoid_high_risk = request.args.get('avoid_high_risk', 'true').lower() == 'true'
    shipment_type = request.args.get('shipment_type', 'medium_heavy')

    if not from_loc or not to_loc:
        return jsonify({'error': 'from and to parameters required'}), 400

    routes = ai_engine.find_alternate_routes(from_loc, to_loc, avoid_high_risk, shipment_type)
    return jsonify({
        'from': from_loc,
        'to': to_loc,
        'shipment_type': shipment_type,
        'routes': routes,
        'generated_at': datetime.utcnow().isoformat()
    })


# ==================== API: DASHBOARD ANALYTICS ====================

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get complete dashboard summary."""
    if WeatherData.query.count() == 0 and District.query.count() > 0:
        seed_weather()

    return jsonify({
        'connectivity': DashboardAnalytics.get_connectivity_summary(),
        'bottlenecks': DashboardAnalytics.get_logistics_bottlenecks(),
        'emergency_routes': DashboardAnalytics.get_emergency_routes(),
        'delivery_status': DashboardAnalytics.get_delivery_status(),
        'weather_summary': DashboardAnalytics.get_weather_summary(),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/dashboard/connectivity', methods=['GET'])
def get_connectivity():
    """Get district-wise connectivity status."""
    return jsonify(DashboardAnalytics.get_connectivity_summary())


@app.route('/api/dashboard/bottlenecks', methods=['GET'])
def get_bottlenecks():
    """Get logistics bottlenecks."""
    return jsonify(DashboardAnalytics.get_logistics_bottlenecks())


@app.route('/api/dashboard/emergency-routes', methods=['GET'])
def get_emergency_routes():
    """Get emergency accessibility routes."""
    return jsonify(DashboardAnalytics.get_emergency_routes())


@app.route('/api/dashboard/deliveries', methods=['GET'])
def get_deliveries():
    """Get delivery status."""
    return jsonify(DashboardAnalytics.get_delivery_status())


# ==================== API: MAP DATA ====================

@app.route('/api/map/all', methods=['GET'])
def get_all_map_data():
    """Get all data needed for the interactive map."""
    return jsonify({
        'districts': [d.to_dict() for d in District.query.all()],
        'roads': [r.to_dict() for r in RoadSegment.query.all()],
        'bridges': [b.to_dict() for b in Bridge.query.all()],
        'vehicles': [v.to_dict() for v in Vehicle.query.all()],
        'field_reports': [r.to_dict() for r in FieldReport.query.all()],
        'alerts': [a.to_dict() for a in Alert.query.filter_by(status='active').all()],
        'weather': [w.to_dict() for w in WeatherData.query.all()]
    })


# ==================== FILE UPLOADS ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for field reports."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/uploads/{filename}'
    })


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== MULTILINGUAL API ====================

TRANSLATIONS = {
    'en': {
        'dashboard': 'Dashboard',
        'map': 'Map',
        'vehicles': 'Vehicles',
        'reports': 'Field Reports',
        'alerts': 'Alerts',
        'routes': 'Route Planner',
        'predictions': 'AI Predictions',
        'route_planner': 'AI Route Planner',
        'risk_filter': 'Risk Filter',
        'from_label': 'From',
        'to_label': 'To',
        'find_routes': 'Find Routes',
        'best_option': 'Best option',
        'risk_level': 'Risk level',
        'of': 'of',
        'total': 'total',
        'network': 'network',
        'critical_issues': 'Critical issues',
        'view_full_map': 'View Full Map',
        'active_alerts': 'Active Alerts',
        'loading_alerts': 'Loading alerts...',
        'no_active_alerts': 'No active alerts',
        'district_connectivity_status': 'District Connectivity Status',
        'top_logistics_bottlenecks': 'Top Logistics Bottlenecks',
        'weather_risk_map': 'Weather Risk Map',
        'essential_supply_tracking': 'Essential Supply Tracking',
        'loading': 'Loading...',
        'no_weather_data': 'No weather data',
        'roads_open': 'roads open',
        'loading_alternates': 'Loading alternates...',
        'no_alternate_routes': 'No alternate routes found.',
        'please_enter_both_locations': 'Please enter both origin and destination locations.',
        'unable_to_calculate_routes': 'Unable to calculate route alternatives.',
        'avoid_high_risk_roads': 'Avoid high-risk roads',
        'include_all_roads': 'Include all roads',
        'normal': 'Normal',
        'moderate': 'Moderate',
        'high': 'High',
        'critical': 'Critical',
        'low': 'Low',
        'on_time': 'On time',
        'delay': 'delay',
        'minutes': 'minutes',
        'km': 'km',
        'min': 'min',
        'risk_score': 'risk score',
        'option': 'Option',
        'use_with_caution': 'USE WITH CAUTION',
        'suggested_routes': 'Suggested Routes',
        'prepare_route_analysis': 'Preparing route analysis...',
        'no_route_data': 'No route data available. Try different locations.',
        'blocked_roads': 'Blocked Roads',
        'open_roads': 'Open Roads',
        'delayed_deliveries': 'Delayed Deliveries',
        'active_vehicles': 'Active Vehicles',
        'critical_alerts': 'Critical Alerts',
        'weather_warning': 'Weather Warning',
        'road_closure': 'Road Closure',
        'flood_alert': 'Flood Alert',
        'landslide_warning': 'Landslide Warning',
        'emergency_route': 'Emergency Route',
        'connectivity_status': 'Connectivity Status',
        'logistics_bottleneck': 'Logistics Bottleneck',
        'delivery_tracking': 'Delivery Tracking',
        'submit_report': 'Submit Report',
        'view_details': 'View Details',
        'alternate_route': 'Alternate Route',
        'estimated_delay': 'Estimated Delay',
        'current_location': 'Current Location',
        'destination': 'Destination',
        'eta': 'Estimated Arrival',
        'status': 'Status',
        'severity': 'Severity',
        'reported_by': 'Reported By',
        'date': 'Date',
        'offline_mode': 'Offline Mode',
        'sync_data': 'Sync Data',
    },
    'hi': {
        'dashboard': 'डैशबोर्ड',
        'map': 'नक्शा',
        'vehicles': 'वाहन',
        'reports': 'फील्ड रिपोर्ट',
        'alerts': 'अलर्ट',
        'routes': 'मार्ग योजनाकार',
        'predictions': 'AI भविष्यवाणी',
        'route_planner': 'एआई मार्ग योजनाकार',
        'risk_filter': 'जोखिम फ़िल्टर',
        'from_label': 'कहाँ से',
        'to_label': 'कहाँ',
        'find_routes': 'मार्ग ढूँढें',
        'best_option': 'सर्वश्रेष्ठ विकल्प',
        'risk_level': 'जोखिम स्तर',
        'of': 'का',
        'total': 'कुल',
        'network': 'नेटवर्क',
        'critical_issues': 'गंभीर मुद्दे',
        'view_full_map': 'पूरा नक्शा देखें',
        'active_alerts': 'सक्रिय अलर्ट',
        'loading_alerts': 'अलर्ट लोड हो रहे हैं...',
        'no_active_alerts': 'कोई सक्रिय अलर्ट नहीं',
        'district_connectivity_status': 'जिला कनेक्टिविटी स्थिति',
        'top_logistics_bottlenecks': 'शीर्ष लॉजिस्टिक्स बाधाएँ',
        'weather_risk_map': 'मौसम जोखिम नक्शा',
        'essential_supply_tracking': 'आवश्यक आपूर्ति ट्रैकिंग',
        'loading': 'लोड हो रहा है...',
        'no_weather_data': 'कोई मौसम डेटा उपलब्ध नहीं',
        'roads_open': 'सड़कें खुली',
        'loading_alternates': 'वैकल्पिक मार्ग लोड हो रहे हैं...',
        'no_alternate_routes': 'कोई वैकल्पिक मार्ग नहीं मिला।',
        'please_enter_both_locations': 'कृपया मूल और गंतव्य दोनों स्थान दर्ज करें।',
        'unable_to_calculate_routes': 'मार्ग विकल्पों की गणना नहीं की जा सकी।',
        'avoid_high_risk_roads': 'उच्च जोखिम वाली सड़कें छोड़ें',
        'include_all_roads': 'सभी सड़कें शामिल करें',
        'normal': 'सामान्य',
        'moderate': 'मध्यम',
        'high': 'उच्च',
        'critical': 'गंभीर',
        'low': 'कम',
        'on_time': 'समय पर',
        'delay': 'देरी',
        'minutes': 'मिनट',
        'km': 'किमी',
        'min': 'मिनट',
        'risk_score': 'जोखिम स्कोर',
        'option': 'विकल्प',
        'use_with_caution': 'सावधानी के साथ उपयोग करें',
        'suggested_routes': 'सुझाए गए मार्ग',
        'prepare_route_analysis': 'मार्ग विश्लेषण तैयार किया जा रहा है...',
        'no_route_data': 'कोई मार्ग डेटा उपलब्ध नहीं है। अलग स्थान आजमाएँ।',
        'blocked_roads': 'अवरुद्ध सड़कें',
        'open_roads': 'खुली सड़कें',
        'delayed_deliveries': 'देरी वाली डिलीवरी',
        'active_vehicles': 'सक्रिय वाहन',
        'critical_alerts': 'गंभीर अलर्ट',
        'weather_warning': 'मौसम चेतावनी',
        'road_closure': 'सड़क बंद',
        'flood_alert': 'बाढ़ अलर्ट',
        'landslide_warning': 'भूस्खलन चेतावनी',
        'emergency_route': 'आपातकालीन मार्ग',
        'connectivity_status': 'कनेक्टिविटी स्थिति',
        'logistics_bottleneck': 'लॉजिस्टिक्स बाधा',
        'delivery_tracking': 'डिलीवरी ट्रैकिंग',
        'submit_report': 'रिपोर्ट जमा करें',
        'view_details': 'विवरण देखें',
        'alternate_route': 'वैकल्पिक मार्ग',
        'estimated_delay': 'अनुमानित देरी',
        'current_location': 'वर्तमान स्थान',
        'destination': 'गंतव्य',
        'eta': 'अनुमानित आगमन',
        'status': 'स्थिति',
        'severity': 'गंभीरता',
        'reported_by': 'रिपोर्टर',
        'date': 'तारीख',
        'offline_mode': 'ऑफलाइन मोड',
        'sync_data': 'डेटा सिंक करें',
    },
    'as': {
        'dashboard': 'ড্যাশবোর্ড',
        'map': 'মানচিত্ৰ',
        'vehicles': 'যানবাহন',
        'reports': 'ফিল্ড ৰিপোৰ্ট',
        'alerts': 'সতৰ্কবাৰ্তা',
        'routes': 'পথ পৰিকল্পনাকাৰী',
        'predictions': 'AI ভৱিষ্যদ্বাণী',
        'route_planner': 'AI পথ পৰিকল্পনাকাৰী',
        'risk_filter': 'জোখিম ফিল্টাৰ',
        'from_label': 'ইয়াৰ পৰা',
        'to_label': 'লৈ',
        'find_routes': 'পথ বিচাৰক',
        'best_option': 'সৰ্বোত্তম বিকল্প',
        'risk_level': 'জোখিম স্তৰ',
        'of': 'ৰ',
        'total': 'মুঠ',
        'network': 'নেটৱৰ্ক',
        'critical_issues': 'গুৰুতৰ সমস্যা',
        'view_full_map': 'সম্পূর্ণ মানচিত্র চাওক',
        'active_alerts': 'সক্ৰিয় সতৰ্কবাৰ্তা',
        'loading_alerts': 'সতৰ্কবাৰ্তা লোড হৈছে...',
        'no_active_alerts': 'কোনো সক্ৰিয় সতৰ্কবাৰ্তা নাই',
        'district_connectivity_status': 'জিলা সংযোগ স্থিতি',
        'top_logistics_bottlenecks': 'শীর্ষ লজিস্টিক্স বাধা',
        'weather_risk_map': 'বতৰ ঝুঁকি মানচিত্র',
        'essential_supply_tracking': 'প্ৰয়োজনীয় সাপ্লাই ট্রেকিং',
        'loading': 'লোড হৈছে...',
        'no_weather_data': 'কোনো বতৰ তথ্য উপলব্ধ নাই',
        'roads_open': 'পথ খোলা',
        'loading_alternates': 'বিকল্প পথ লোড হৈছে...',
        'no_alternate_routes': 'কোনো বিকল্প পথ পোৱা নগল।',
        'please_enter_both_locations': 'ক্ৰিপা কৰি মূল আৰু গন্তব্য দুটো স্থান দিয়া কৰক।',
        'unable_to_calculate_routes': 'পথ বিকল্প গণনা কৰিব পৰা নগল।',
        'avoid_high_risk_roads': 'উচ্চ ঝুঁকিপূর্ণ পথ এড়িয়ে যাওক',
        'include_all_roads': 'সকলো পথ অন্তৰ্ভুক্ত কৰক',
        'normal': 'স্বাভাবিক',
        'moderate': 'মধ্যম',
        'high': 'উচ্চ',
        'critical': 'গুৰুতৰ',
        'low': 'কম',
        'on_time': 'সঠিক সময়ে',
        'delay': 'বিলম্ব',
        'minutes': 'মিনিট',
        'km': 'কিমি',
        'min': 'মিনিট',
        'risk_score': 'জোখিম স্কোৰ',
        'option': 'বিকল্প',
        'use_with_caution': 'সাৱধানীৰ সৈতে ব্যৱহাৰ কৰক',
        'suggested_routes': 'প্রস্তাবিত পথ',
        'prepare_route_analysis': 'পথ বিশ্লেষণ প্ৰস্তুত হৈছে...',
        'no_route_data': 'কোনো পথ তথ্য উপলব্ধ নাই। অন্য ঠাই চেষ্টা কৰক।',
        'blocked_roads': 'বন্ধ পথ',
        'open_roads': 'খোলা পথ',
        'delayed_deliveries': 'বিলম্বিত প্ৰেৰণ',
        'active_vehicles': 'সক্ৰিয় যানবাহন',
        'critical_alerts': 'গুৰুতৰ সতৰ্কবাৰ্তা',
        'weather_warning': 'বতৰ সতৰ্কবাৰ্তা',
        'road_closure': 'পথ বন্ধ',
        'flood_alert': 'বানপানী সতৰ্কবাৰ্তা',
        'landslide_warning': 'ভূমিস্খলন সতৰ্কবাৰ্তা',
        'emergency_route': 'জৰুৰীকালীন পথ',
        'connectivity_status': 'সংযোগ স্থিতি',
        'logistics_bottleneck': 'পৰিবহন বাধা',
        'delivery_tracking': 'প্ৰেৰণ ট্ৰেকিং',
        'submit_report': 'ৰিপোৰ্ট দাখিল কৰক',
        'view_details': 'বিশদ চাওক',
        'alternate_route': 'বিকল্প পথ',
        'estimated_delay': 'আনুমানিক বিলম্ব',
        'current_location': 'বৰ্তমান স্থান',
        'destination': 'গন্তব্য',
        'eta': 'আনুমানিক আগমণ',
        'status': 'স্থিতি',
        'severity': 'গুৰুত্ব',
        'reported_by': 'ৰিপোৰ্টকাৰী',
        'date': 'তাৰিখ',
        'offline_mode': 'অফলাইন মোড',
        'sync_data': 'ডাটা ছিংক কৰক',
    }
}


@app.route('/api/translations/<lang>', methods=['GET'])
def get_translations(lang):
    """Get translations for a language."""
    return jsonify(TRANSLATIONS.get(lang, TRANSLATIONS['en']))


# ==================== OFFLINE SYNC API ====================

@app.route('/api/sync/offline-data', methods=['POST'])
def sync_offline_data():
    """Sync offline data collected in low-network areas."""
    data = request.get_json()
    synced_items = []

    for report_data in data.get('reports', []):
        report = FieldReport(
            report_type=report_data.get('report_type', 'other'),
            title=report_data.get('title', ''),
            description=report_data.get('description', ''),
            lat=report_data.get('lat', 0.0),
            lng=report_data.get('lng', 0.0),
            location_name=report_data.get('location_name', ''),
            photo_url=report_data.get('photo_url', ''),
            severity=report_data.get('severity', 'medium'),
            reported_by=report_data.get('reported_by', ''),
            reporter_phone=report_data.get('reporter_phone', ''),
            reporter_designation=report_data.get('reporter_designation', ''),
            district_id=report_data.get('district_id'),
            reported_at=datetime.fromisoformat(report_data.get('reported_at')) if report_data.get('reported_at') else datetime.utcnow()
        )
        db.session.add(report)
        synced_items.append(report.to_dict())

    db.session.commit()
    return jsonify({
        'success': True,
        'synced_count': len(synced_items),
        'items': synced_items
    })


@app.route('/api/sync/fetch-offline', methods=['GET'])
def fetch_offline_data():
    """Fetch data needed for offline operation."""
    return jsonify({
        'districts': [d.to_dict() for d in District.query.all()],
        'roads': [r.to_dict() for r in RoadSegment.query.all()],
        'bridges': [b.to_dict() for b in Bridge.query.all()],
        'alerts': [a.to_dict() for a in Alert.query.filter_by(status='active').all()],
        'weather': [w.to_dict() for w in WeatherData.query.all()],
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed if empty
        if not District.query.first():
            seed_all_data()
    app.run(debug=True, host='0.0.0.0', port=3242)
