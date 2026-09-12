"""
NER Logistics Accessibility Intelligence Platform - AI/ML Engine
Provides route disruption prediction, alternate routing, risk scoring, and ETA estimation.
"""
import math
import json
from datetime import datetime, timedelta
from models import RoadSegment, Bridge, WeatherData, Vehicle, Alert, District, db


class RoutePredictionEngine:
    """AI engine for predicting route disruptions and suggesting alternates."""

    AIR_COST_MULTIPLIER = 3.5
    SHIPMENT_PRICING = {
        'small_pickup': {'label': 'Mini / Small Pickup (0.5-2 tons)', 'min': 22, 'max': 35},
        'light_commercial': {'label': 'Light Commercial Vehicle (3-5 tons)', 'min': 30, 'max': 45},
        'medium_heavy': {'label': 'Medium & Heavy Truck (7-16 tons)', 'min': 40, 'max': 65},
        'large_container': {'label': 'Multi-Axle / Large Container (20-40 tons)', 'min': 60, 'max': 90}
    }

    def __init__(self):
        self.risk_weights = {
            'rainfall': 0.25,
            'terrain': 0.20,
            'road_condition': 0.20,
            'traffic': 0.10,
            'bridge_status': 0.15,
            'historical': 0.10
        }

    def calculate_road_risk(self, road):
        """Calculate composite risk score for a road segment (0-1 scale)."""
        risk = 0.0

        # Rainfall factor
        weather = WeatherData.query.filter_by(district_id=road.district_id).order_by(
            WeatherData.recorded_at.desc()).first()
        if weather:
            rainfall = weather.rainfall_mm or 0
            if rainfall > 100:
                risk += self.risk_weights['rainfall'] * 1.0
            elif rainfall > 50:
                risk += self.risk_weights['rainfall'] * 0.7
            elif rainfall > 20:
                risk += self.risk_weights['rainfall'] * 0.4
            else:
                risk += self.risk_weights['rainfall'] * 0.1

        # Terrain factor
        terrain_risk = {
            'plains': 0.1,
            'hilly': 0.5,
            'mountainous': 0.8
        }
        risk += self.risk_weights['terrain'] * terrain_risk.get(road.terrain_type, 0.5)

        # Road condition factor
        condition_risk = {
            'good': 0.1,
            'fair': 0.4,
            'poor': 0.8
        }
        risk += self.risk_weights['road_condition'] * condition_risk.get(road.condition, 0.5)

        # Traffic factor
        traffic_risk = {
            'none': 0.0,
            'light': 0.1,
            'normal': 0.2,
            'moderate': 0.4,
            'heavy': 0.6
        }
        risk += self.risk_weights['traffic'] * traffic_risk.get(road.traffic_level, 0.2)

        # Historical incidents on this route
        recent_alerts = Alert.query.filter(
            Alert.affected_districts.contains(road.from_location) |
            Alert.affected_districts.contains(road.to_location)
        ).filter(Alert.created_at > datetime.utcnow() - timedelta(days=7)).count()
        risk += self.risk_weights['historical'] * min(recent_alerts * 0.15, 1.0)

        # Bridge status check along this route
        bridges = Bridge.query.filter_by(district_id=road.district_id).all()
        bridge_risk = 0.0
        for bridge in bridges:
            if bridge.status == 'closed':
                bridge_risk = 1.0
                break
            elif bridge.status == 'partial':
                bridge_risk = max(bridge_risk, 0.5)
            elif bridge.condition == 'poor':
                bridge_risk = max(bridge_risk, 0.4)
        risk += self.risk_weights['bridge_status'] * bridge_risk

        if road.status == 'blocked':
            return 1.0
        if road.status == 'partial':
            return max(risk, 0.75)
        return min(risk, 1.0)

    def predict_disruptions(self, hours_ahead=24):
        """Predict likely route disruptions in the next N hours."""
        predictions = []
        roads = RoadSegment.query.all()

        for road in roads:
            risk = self.calculate_road_risk(road)
            weather = WeatherData.query.filter_by(district_id=road.district_id).order_by(
                WeatherData.recorded_at.desc()).first()

            triggered_by_status = road.status in ['blocked', 'partial']
            triggered_by_condition = road.condition in ['poor', 'fair'] and road.terrain_type in ['hilly', 'mountainous']
            triggered_by_weather = bool(weather and weather.rainfall_mm >= 30)

            if risk > 0.7 or triggered_by_status or triggered_by_condition or triggered_by_weather:
                disruption_type = self._determine_disruption_type(road, weather)
                delay_estimate = self._estimate_delay(road, risk)

                predictions.append({
                    'road_id': road.id,
                    'road_name': road.name,
                    'from': road.from_location,
                    'to': road.to_location,
                    'risk_score': round(risk, 2),
                    'predicted_disruption': disruption_type,
                    'confidence': 'high' if risk > 0.85 or triggered_by_status else 'medium' if risk > 0.7 or triggered_by_condition or triggered_by_weather else 'low',
                    'estimated_delay_minutes': delay_estimate,
                    'recommended_action': self._recommend_action(risk, disruption_type),
                    'weather_data': weather.to_dict() if weather else None,
                    'coordinates': {
                        'from': {'lat': road.from_lat, 'lng': road.from_lng},
                        'to': {'lat': road.to_lat, 'lng': road.to_lng}
                    }
                })

        predictions.sort(key=lambda x: x['risk_score'], reverse=True)
        return predictions[:20]

    def _determine_disruption_type(self, road, weather):
        """Determine the most likely disruption type based on conditions."""
        if road.status == 'blocked':
            return 'road_closure'
        if weather and weather.rainfall_mm > 80:
            if road.terrain_type in ['hilly', 'mountainous']:
                return 'landslide'
            else:
                return 'flood'
        elif weather and weather.rainfall_mm > 30:
            if road.condition == 'poor':
                return 'road_damage'
            else:
                return 'water_logging'
        elif road.condition == 'poor':
            return 'road_failure'
        elif weather and weather.weather_condition == 'snow_rain':
            return 'snow_blockage'
        else:
            return 'traffic_congestion'

    def _estimate_delay(self, road, risk):
        """Estimate delay in minutes based on risk and road length."""
        base_delay = 15  # minimum delay
        risk_multiplier = risk * 3  # 0-3x multiplier
        length_factor = road.length_km / 50  # longer roads = longer delays
        return int(base_delay + (risk_multiplier * 60 * length_factor))

    def _recommend_action(self, risk, disruption_type):
        """Generate AI recommendation based on risk level."""
        if risk > 0.9:
            return 'ROUTE CLOSURE RECOMMENDED - Deploy emergency response teams, issue public advisory'
        elif risk > 0.8:
            return 'HEAVY RESTRICTION - Consider alternate routes, restrict heavy vehicles, enhance monitoring'
        elif risk > 0.7:
            return 'CAUTION REQUIRED - Reduce speed limits, deploy warning signage, monitor closely'
        else:
            return 'NORMAL PRECAUTIONS - Standard safety measures sufficient'

    def find_alternate_routes(self, from_loc, to_loc, avoid_high_risk=True, shipment_type='medium_heavy'):
        """Find alternate routes between two locations using simple pathfinding."""
        pricing = self.SHIPMENT_PRICING.get(shipment_type, self.SHIPMENT_PRICING['medium_heavy'])
        all_roads = RoadSegment.query.all()

        # Keep older databases compatible with the expanded NER corridor graph.
        if not any(
            {road.from_location, road.to_location} == {'Churachandpur', 'Aizawl'}
            for road in all_roads
        ):
            all_roads.append(RoadSegment(
                name='NH-102B Churachandpur-Aizawl',
                from_location='Churachandpur',
                to_location='Aizawl',
                from_lat=24.3333,
                from_lng=93.6833,
                to_lat=23.7367,
                to_lng=92.7146,
                road_type='national_highway',
                length_km=190.0,
                status='open',
                condition='fair',
                terrain_type='hilly',
                risk_score=0.55,
                weather_impact='none',
                traffic_level='moderate'
            ))

        # Build adjacency list
        graph = {}
        for road in all_roads:
            if road.from_location not in graph:
                graph[road.from_location] = []
            if road.to_location not in graph:
                graph[road.to_location] = []

            risk = self.calculate_road_risk(road)
            weight = road.length_km * (1 + risk * 2) if avoid_high_risk else road.length_km

            graph[road.from_location].append({
                'to': road.to_location,
                'road': road,
                'weight': weight,
                'risk': risk,
                'status': road.status,
                'road_key': road.id or f'{road.name}|{road.from_location}|{road.to_location}'
            })
            # Bidirectional
            graph[road.to_location].append({
                'to': road.from_location,
                'road': road,
                'weight': weight,
                'risk': risk,
                'status': road.status,
                'road_key': road.id or f'{road.name}|{road.from_location}|{road.to_location}'
            })

        known_locations = {location.casefold(): location for location in graph}
        source = known_locations.get(from_loc.strip().casefold())
        destination = known_locations.get(to_loc.strip().casefold())
        if not source or not destination:
            return []

        # Always search for usable routes first. A longer open route is safer
        # than presenting a blocked route as the only practical choice.
        routes = self._search_route_paths(graph, source, destination, True)
        if routes:
            relaxed_routes = self._search_route_paths(graph, source, destination, False)
            known_paths = {self._route_key(route) for route in routes}
            routes.extend(
                route for route in relaxed_routes
                if self._route_key(route) not in known_paths
            )
        else:
            routes = self._search_route_paths(graph, source, destination, False)

        # If the network is disconnected for the requested origin/destination,
        # use an air corridor so the planner still gives a usable alternative.
        if not routes:
            return self._rank_routes([self._build_air_route(source, destination)], pricing)

        # Format routes with details
        result = []
        for route in routes:
            route_details = self._build_route_details(route['path'], graph, route['edges'])
            result.append(route_details)

        if not any(not route.get('blocked') for route in result):
            result.append(self._build_air_route(source, destination))

        return self._rank_routes(result, pricing)

    def _search_route_paths(self, graph, source, destination, avoid_blocked):
        """Return up to five distinct simple paths ordered by search cost."""
        import heapq
        import itertools

        sequence = itertools.count()
        queue = [(0, next(sequence), source, [], [])]
        routes = []
        seen_paths = set()
        while queue:
            cost, _, current, path, edges = heapq.heappop(queue)
            new_path = path + [current]

            if current == destination:
                path_key = tuple(edge['road_key'] for edge in edges)
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    routes.append({'cost': cost, 'path': new_path, 'edges': edges})
                continue

            for edge in graph.get(current, []):
                if edge['to'] in new_path:
                    continue
                if edge['status'] == 'blocked' and avoid_blocked:
                    continue
                heapq.heappush(queue, (
                    cost + edge['weight'],
                    next(sequence),
                    edge['to'],
                    new_path,
                    edges + [edge]
                ))

        return routes

    def _route_key(self, route):
        """Identify a route by its actual highway edges, not only its nodes."""
        return tuple(edge['road_key'] for edge in route.get('edges', []))

    def _rank_routes(self, routes, pricing=None):
        """Rank routes using safety, speed, and estimated transport cost."""
        if not routes:
            return []

        pricing = pricing or self.SHIPMENT_PRICING['medium_heavy']
        base_cost_per_km = (pricing['min'] + pricing['max']) / 2
        fastest_time = min(max(route.get('estimated_time_minutes', 1), 1) for route in routes)
        for route in routes:
            if 'estimated_cost_inr' not in route:
                is_air_route = any(
                    segment.get('road_type') == 'air_route'
                    for segment in route.get('segments', [])
                )
                cost_rate = base_cost_per_km * (
                    self.AIR_COST_MULTIPLIER if is_air_route else 1
                )
                route['estimated_cost_inr'] = max(
                    base_cost_per_km,
                    round(route.get('total_distance_km', 0) * cost_rate)
                )
            route['cost_per_km_inr'] = round(
                route['estimated_cost_inr'] / max(route.get('total_distance_km', 1), 1),
                2
            )

        for route in routes:
            risk = max(0.0, min(float(route.get('average_risk', 1.0)), 1.0))
            cost_efficiency_score = round(min(
                100,
                (50 * base_cost_per_km) / max(route['cost_per_km_inr'], 1)
            ), 1)
            if route.get('blocked'):
                safety_score = 0
                speed_score = 0
                cost_score = 0
            else:
                safety_score = round((1 - risk) * 40, 1)
                speed_score = round(min(20, (fastest_time / max(route.get('estimated_time_minutes', 1), 1)) * 20), 1)
                cost_score = round(cost_efficiency_score * 0.4, 1)
            route['safety_score'] = safety_score
            route['speed_score'] = speed_score
            route['cost_score'] = cost_score
            route['cost_efficiency_score'] = cost_efficiency_score if not route.get('blocked') else 0
            route['route_score'] = round(safety_score + cost_score + speed_score, 1)

        return sorted(
            routes,
            key=lambda route: (route['route_score'], route['safety_score'], -route['estimated_time_minutes']),
            reverse=True
        )

    def _build_fallback_route(self, from_loc, to_loc):
        """Build a best-effort route when the graph has no connected path."""
        from_district = None
        to_district = None
        for district in District.query.all():
            if district.name.lower() == from_loc.lower():
                from_district = district
            if district.name.lower() == to_loc.lower():
                to_district = district

        from_lat = from_district.lat if from_district else 25.5
        from_lng = from_district.lng if from_district else 92.5
        to_lat = to_district.lat if to_district else 27.0
        to_lng = to_district.lng if to_district else 93.5

        if from_district and to_district:
            distance_km = math.hypot(
                (to_lat - from_lat) * 111,
                (to_lng - from_lng) * 102
            )
        else:
            distance_km = 120
        distance_km = max(1, round(distance_km, 1))
        estimated_time = max(15, int((distance_km / 40) * 60))
        average_risk = round(min(0.85, 0.45 + (distance_km / 1000)), 2)
        segments = [{
            'from': from_loc,
            'to': to_loc,
            'road_name': 'Regional corridor fallback',
            'distance_km': distance_km,
            'status': 'partial',
            'condition': 'fair',
            'risk_score': round(average_risk, 2),
            'coordinates': {
                'from': {'lat': from_lat, 'lng': from_lng},
                'to': {'lat': to_lat, 'lng': to_lng}
            }
        }]

        return {
            'path': [from_loc, to_loc],
            'segments': segments,
            'total_distance_km': distance_km,
            'average_risk': average_risk,
            'estimated_time_minutes': estimated_time,
            'recommendation': 'USE WITH CAUTION'
        }

    def _build_air_route(self, from_loc, to_loc):
        """Build a direct air corridor when every road route is blocked."""
        districts = {district.name: district for district in District.query.all()}
        from_district = districts.get(from_loc)
        to_district = districts.get(to_loc)

        if not from_district or not to_district:
            return self._build_fallback_route(from_loc, to_loc)

        distance_km = max(1, round(math.hypot(
            (to_district.lat - from_district.lat) * 111,
            (to_district.lng - from_district.lng) * 102
        ), 1))
        estimated_time = max(20, int((distance_km / 650) * 60) + 45)
        return {
            'path': [from_loc, to_loc],
            'segments': [{
                'from': from_loc,
                'to': to_loc,
                'road_name': f'Air corridor {from_loc}-{to_loc}',
                'road_type': 'air_route',
                'distance_km': distance_km,
                'status': 'available',
                'condition': 'good',
                'risk_score': 0.15,
                'coordinates': {
                    'from': {'lat': from_district.lat, 'lng': from_district.lng},
                    'to': {'lat': to_district.lat, 'lng': to_district.lng}
                },
                'weather': self._latest_weather(from_district.id)
            }],
            'total_distance_km': distance_km,
            'average_risk': 0.15,
            'estimated_time_minutes': estimated_time,
            'recommendation': 'AIR ROUTE - NO OPEN ROAD',
            'blocked': False
        }

    def _latest_weather(self, district_id):
        """Return the latest stored weather observation for a district."""
        weather = WeatherData.query.filter_by(district_id=district_id).order_by(
            WeatherData.recorded_at.desc()
        ).first()
        return weather.to_dict() if weather else None

    def _build_route_details(self, path, graph, selected_edges=None):
        """Build detailed route information from path nodes."""
        segments = []
        total_distance = 0
        total_risk = 0
        estimated_time = 0
        blocked = False

        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]

            edge = selected_edges[i] if selected_edges and i < len(selected_edges) else next(
                (candidate for candidate in graph.get(from_node, []) if candidate['to'] == to_node),
                None
            )
            if edge:
                road = edge['road']
                weather = self._latest_weather(road.district_id)
                segments.append({
                    'from': from_node,
                    'to': to_node,
                    'road_name': road.name,
                    'road_type': road.road_type,
                    'distance_km': road.length_km,
                    'status': road.status,
                    'condition': road.condition,
                    'terrain_type': road.terrain_type,
                    'risk_score': round(edge['risk'], 2),
                    'coordinates': {
                        'from': {'lat': road.from_lat, 'lng': road.from_lng},
                        'to': {'lat': road.to_lat, 'lng': road.to_lng}
                    },
                    'weather': weather
                })
                total_distance += road.length_km
                total_risk += edge['risk']
                blocked = blocked or road.status == 'blocked'
                # Estimate time based on road condition and traffic
                avg_speed = 40 if road.condition == 'good' else 25 if road.condition == 'fair' else 15
                estimated_time += (road.length_km / avg_speed) * 60

        average_risk = round(total_risk / len(segments), 2) if segments else 0
        if blocked:
            recommendation = 'BLOCKED - AVOID ROUTE'
        elif average_risk < 0.4:
            recommendation = 'RECOMMENDED'
        elif average_risk < 0.7:
            recommendation = 'USE WITH CAUTION'
        else:
            recommendation = 'HIGH RISK'

        return {
            'path': path,
            'segments': segments,
            'total_distance_km': round(total_distance, 1),
            'average_risk': average_risk,
            'estimated_time_minutes': int(estimated_time),
            'recommendation': recommendation,
            'blocked': blocked
        }

    def estimate_eta(self, vehicle_id):
        """Estimate arrival time for a vehicle considering current conditions."""
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return None

        # Find route from current position to destination
        routes = self.find_alternate_routes(
            vehicle.origin or 'Unknown',
            vehicle.destination or 'Unknown',
            avoid_high_risk=False
        )

        if not routes:
            return {
                'vehicle_id': vehicle_id,
                'estimated_arrival': None,
                'delay_minutes': 0,
                'confidence': 'low',
                'message': 'No route data available for destination'
            }

        best_route = routes[0]
        base_time = best_route['estimated_time_minutes']

        # Add delays from active disruptions
        delay = 0
        for segment in best_route['segments']:
            if segment['status'] == 'blocked':
                delay += 120  # 2 hours for blocked roads
            elif segment['status'] == 'partial':
                delay += 45  # 45 minutes for partial blocks
            elif segment['risk_score'] > 0.7:
                delay += 30

        weather = WeatherData.query.filter_by(district_id=vehicle.district_id).order_by(
            WeatherData.recorded_at.desc()).first()
        if weather and weather.rainfall_mm > 50:
            delay += int(weather.rainfall_mm * 0.5)

        confidence = 'high' if delay < 30 else 'medium' if delay < 90 else 'low'
        eta = datetime.utcnow() + timedelta(minutes=base_time + delay)

        return {
            'vehicle_id': vehicle_id,
            'vehicle_number': vehicle.vehicle_number,
            'destination': vehicle.destination,
            'base_time_minutes': base_time,
            'delay_minutes': delay,
            'estimated_arrival': eta.isoformat(),
            'confidence': confidence,
            'route_risk': best_route['average_risk'],
            'message': f"Expected delay: {delay} minutes due to current conditions."
        }


class DashboardAnalytics:
    """Generate analytics for the centralized dashboard."""

    @staticmethod
    def get_connectivity_summary():
        """Get district-wise connectivity status summary."""
        districts = District.query.all()
        summary = {
            'total_districts': len(districts),
            'normal': 0,
            'warning': 0,
            'critical': 0,
            'districts': []
        }

        for d in districts:
            roads = RoadSegment.query.filter_by(district_id=d.id).all()
            open_roads = sum(1 for r in roads if r.status == 'open')
            total_roads = len(roads)
            bridges = Bridge.query.filter_by(district_id=d.id).all()
            open_bridges = sum(1 for b in bridges if b.status == 'operational')

            summary[d.connectivity_status] += 1
            summary['districts'].append({
                'id': d.id,
                'name': d.name,
                'state': d.state,
                'status': d.connectivity_status,
                'lat': d.lat,
                'lng': d.lng,
                'total_roads': total_roads,
                'open_roads': open_roads,
                'blocked_roads': total_roads - open_roads,
                'total_bridges': len(bridges),
                'open_bridges': open_bridges,
                'connectivity_percentage': round((open_roads / total_roads * 100), 1) if total_roads else 0
            })

        return summary

    @staticmethod
    def get_logistics_bottlenecks():
        """Identify current logistics bottlenecks."""
        bottlenecks = []

        # Blocked roads
        blocked_roads = RoadSegment.query.filter_by(status='blocked').all()
        for road in blocked_roads:
            bottlenecks.append({
                'type': 'road_block',
                'name': road.name,
                'location': f"{road.from_location} - {road.to_location}",
                'severity': 'critical',
                'impact': f"{road.length_km} km affected",
                'reason': road.block_reason or 'Unknown',
                'since': road.block_since.isoformat() if road.block_since else None,
                'estimated_clearance': road.estimated_reopen.isoformat() if road.estimated_reopen else None
            })

        # Closed bridges
        closed_bridges = Bridge.query.filter(Bridge.status != 'operational').all()
        for bridge in closed_bridges:
            bottlenecks.append({
                'type': 'bridge_issue',
                'name': bridge.name,
                'location': bridge.river_name or 'Unknown',
                'severity': 'high' if bridge.status == 'closed' else 'medium',
                'impact': f"Load capacity: {bridge.load_capacity_tons} tons",
                'reason': f"Bridge {bridge.status}",
                'since': None,
                'estimated_clearance': None
            })

        # Delayed vehicles
        delayed_vehicles = Vehicle.query.filter_by(status='delayed').all()
        for vehicle in delayed_vehicles:
            bottlenecks.append({
                'type': 'delivery_delay',
                'name': vehicle.vehicle_number,
                'location': vehicle.destination,
                'severity': 'high',
                'impact': f"{vehicle.cargo_type}: {vehicle.cargo_description}",
                'reason': 'Route disruption / Weather',
                'since': vehicle.last_update.isoformat() if vehicle.last_update else None,
                'estimated_clearance': None
            })

        # Ecological zones: hilly and mountainous corridors have elevated
        # wildlife-crossing risk, especially where traffic is moving slowly.
        ecological_roads = RoadSegment.query.filter(
            RoadSegment.terrain_type.in_(['hilly', 'mountainous']),
            RoadSegment.status.in_(['open', 'partial'])
        ).all()
        for road in ecological_roads:
            mountainous = road.terrain_type == 'mountainous'
            bottlenecks.append({
                'type': 'wildlife_crossing',
                'name': f'Wildlife Crossing Risk: {road.name}',
                'location': f'{road.from_location} - {road.to_location}',
                'severity': 'high' if mountainous else 'medium',
                'impact': 'High probability of animals crossing the road',
                'reason': 'Ecological zone / wildlife movement corridor',
                'wildlife_risk': 'high' if mountainous else 'moderate',
                'since': None,
                'estimated_clearance': None
            })

        bottlenecks.sort(key=lambda x: {'critical': 0, 'high': 1, 'medium': 2}.get(x['severity'], 3))
        return bottlenecks

    @staticmethod
    def get_emergency_routes():
        """Get current emergency and disaster-time accessibility routes."""
        emergency_routes = []

        # Find all open routes that can serve as emergency corridors
        open_roads = RoadSegment.query.filter_by(status='open').filter(
            RoadSegment.road_type.in_(['national_highway', 'state_highway'])
        ).all()

        for road in open_roads:
            risk = RoutePredictionEngine().calculate_road_risk(road)
            if risk < 0.5:  # Only low-risk routes for emergency
                emergency_routes.append({
                    'road_id': road.id,
                    'name': road.name,
                    'from': road.from_location,
                    'to': road.to_location,
                    'length_km': road.length_km,
                    'road_type': road.road_type,
                    'risk_score': round(risk, 2),
                    'suitable_for': ['ambulance', 'fire', 'relief'] if road.road_type == 'national_highway' else ['relief', 'supply'],
                    'coordinates': {
                        'from': {'lat': road.from_lat, 'lng': road.from_lng},
                        'to': {'lat': road.to_lat, 'lng': road.to_lng}
                    }
                })

        emergency_routes.sort(key=lambda x: x['risk_score'])
        return emergency_routes[:15]

    @staticmethod
    def get_delivery_status():
        """Get real-time delivery status of essential supplies."""
        vehicles = Vehicle.query.all()
        status = {
            'total': len(vehicles),
            'active': 0,
            'delayed': 0,
            'completed': 0,
            'by_cargo_type': {},
            'vehicles': []
        }

        for v in vehicles:
            status[v.status] = status.get(v.status, 0) + 1

            cargo = v.cargo_type or 'unknown'
            if cargo not in status['by_cargo_type']:
                status['by_cargo_type'][cargo] = {'total': 0, 'active': 0, 'delayed': 0}
            status['by_cargo_type'][cargo]['total'] += 1
            status['by_cargo_type'][cargo][v.status] = status['by_cargo_type'][cargo].get(v.status, 0) + 1

            # Calculate progress
            engine = RoutePredictionEngine()
            eta_info = engine.estimate_eta(v.id)

            status['vehicles'].append({
                'id': v.id,
                'vehicle_number': v.vehicle_number,
                'cargo_type': v.cargo_type,
                'cargo_description': v.cargo_description,
                'status': v.status,
                'origin': v.origin,
                'destination': v.destination,
                'current_position': {'lat': v.current_lat, 'lng': v.current_lng},
                'speed_kmh': v.speed_kmh,
                'driver': v.driver_name,
                'eta': eta_info['estimated_arrival'] if eta_info else None,
                'delay_minutes': eta_info['delay_minutes'] if eta_info else 0
            })

        return status

    @staticmethod
    def get_weather_summary():
        """Get weather summary across NER."""
        weather_data = WeatherData.query.all()
        summary = {
            'total_locations': len(weather_data),
            'critical': 0,
            'high_risk': 0,
            'moderate': 0,
            'low': 0,
            'locations': []
        }

        for w in weather_data:
            risk_level = 'critical' if w.rainfall_mm > 80 or w.landslide_risk == 'critical' else \
                        'high_risk' if w.rainfall_mm > 50 or w.flood_risk == 'high' else \
                        'moderate' if w.rainfall_mm > 20 else 'low'
            summary[risk_level] = summary.get(risk_level, 0) + 1

            risk_score = 0
            if risk_level == 'critical':
                risk_score = 90 + min(10, max(0, w.rainfall_mm / 20))
            elif risk_level == 'high_risk':
                risk_score = 70 + min(20, max(0, w.rainfall_mm / 10))
            elif risk_level == 'moderate':
                risk_score = 40 + min(30, max(0, w.rainfall_mm / 5))
            else:
                risk_score = 10 + min(20, max(0, w.rainfall_mm / 10))

            summary['locations'].append({
                'district_id': w.district_id,
                'location': w.location_name,
                'temperature': w.temperature,
                'rainfall_mm': w.rainfall_mm,
                'weather_condition': w.weather_condition,
                'flood_risk': w.flood_risk,
                'landslide_risk': w.landslide_risk,
                'visibility_km': w.visibility_km,
                'risk_level': risk_level,
                'risk_score': round(min(risk_score, 100), 1),
                'lat': w.lat,
                'lng': w.lng
            })

        return summary
