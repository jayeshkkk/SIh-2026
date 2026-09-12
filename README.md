# Road Management & Monitoring Dashboard 🛣️

A full-stack web application built for smart road infrastructure management — 
combining real-time tracking, geospatial visualization, and predictive analytics 
into a single dashboard.

## What it does
- 🗺️ **GIS Maps** — interactive road and route visualization using Leaflet.js
- 🚗 **Vehicle Tracking** — real-time monitoring of vehicles on the road network
- 📊 **Analytics** — data-driven insights into road usage and conditions
- 🌦️ **Weather Risk Analysis** — flags routes with weather-related risk factors
- 🧭 **Route Planning** — suggests optimal routes based on live conditions
- 🤖 **AI Predictions** — predictive modeling for road/traffic risk
- 📋 **Field Reports** — logging and reviewing on-ground reports
- 🚨 **Alerts** — real-time alerting system for road incidents

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-CORS
- **Frontend:** Jinja2 templating with a shared `base.html` layout, Leaflet.js for maps
- **Database:** SQLAlchemy ORM

## Why I built this
Built as part of Smart India Hackathon (SIH), aimed at solving real problems in 
road infrastructure monitoring using accessible, open-source web technologies.

## Setup
\`\`\`bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
flask run
\`\`\`
