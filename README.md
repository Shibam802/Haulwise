# Haulwise — Trip & ELD Log Planner

A full-stack application that plans truck routes and automatically generates FMCSA HOS-based daily driver logs, given a starting point, pickup location, drop-off location, and the hours already used in the driver's current duty cycle.

**Live Demo:** [https://haulwise-tawny.vercel.app/](https://haulwise-tawny.vercel.app/)  
**Backend API:** [https://haulwise-kg4g.onrender.com](https://haulwise-kg4g.onrender.com)

> **Note:** The backend runs on Render's free tier and may spin down when idle. The first request after a period of inactivity can take 30–60 seconds while the service wakes up. This is expected behavior.

---

## 🚛 What It Does

Long-haul truck drivers must operate within federal Hours-of-Service (HOS) requirements when planning a trip. Drivers need to account for driving limits, on-duty windows, mandatory breaks, rest periods, fuel stops, and the limits of their weekly duty cycle.

Haulwise automates this planning process.

### 1. 📍 Location Geocoding
The application converts locations into geographic coordinates using **OpenStreetMap Nominatim**:
- Current location
- Pickup location
- Drop-off location

### 2. 🗺️ Route Planning
Haulwise uses the **OSRM routing engine** to calculate:
- Driving route
- Total distance
- Estimated driving duration
- Route geometry for map visualization

### 3. ⏱️ HOS-Based Trip Simulation
The backend simulates the driver's duty schedule while considering:
- **11-hour** driving limit
- **14-hour** on-duty window
- Mandatory **30-minute break** after 8 hours of driving
- **10-hour off-duty reset** between duty periods
- **70-hour / 8-day cycle** tracking
- Simulated **34-hour restart** when the cycle limit is reached
- Fuel stop approximately every **1,000 miles**
- **1 hour** allocated for pickup
- **1 hour** allocated for drop-off

### 4. 📊 ELD Log Generation
The generated schedule is visualized as:
- Interactive route map with Leaflet
- Pickup, drop-off, fuel, and rest stop markers
- Day-by-day driving schedule
- SVG-based daily ELD log sheets showing duty status transitions across a 24-hour grid

---

## 🧠 Engineering Highlight

The main engineering challenge of Haulwise is a **discrete-event HOS simulation engine**.

Multiple constraints can become active at approximately the same time:
$$\text{Driving Limit} \longrightarrow \text{Mandatory Break} \longrightarrow \text{Fuel Stop} \longrightarrow \text{14-Hour Duty Window} \longrightarrow \text{70-Hour Cycle Limit}$$

Instead of relying on fixed schedules, the backend continuously evaluates the driver's state and determines which constraint is reached first. This makes the project a practical example of:
- Constraint-based scheduling
- State-machine design
- Discrete-event simulation
- Route-aware time/distance calculations

The primary simulation logic is implemented in `backend/trip/hos_engine.py`.

---

## 📸 Screenshots / Demo

<img width="1877" height="987" alt="image" src="https://github.com/user-attachments/assets/180fd80a-ac04-49e0-b328-83c313ebee55" />


<img width="1885" height="982" alt="image" src="https://github.com/user-attachments/assets/a4941ee8-bd45-40b1-bf01-ccabbbc3fb06" />

<img width="1875" height="767" alt="image" src="https://github.com/user-attachments/assets/b6956c72-6658-4cfc-8308-d17755add961" />

> **Setup Note:** Ensure images are placed inside `screenshots/haulwise-map.png` and `screenshots/haulwise-eld-log.png`.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    │   Trip Information  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React + Vite      │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                           HTTP POST
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Django REST API    │
                    │   /api/plan-trip/   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐           ┌─────────────────┐
       │   Nominatim     │           │      OSRM       │
       │   Geocoding     │           │  Route Engine   │
       └────────┬────────┘           └────────┬────────┘
                │                             │
                └─────────────┬───────────────┘
                              ▼
                    ┌─────────────────────┐
                    │     HOS Engine      │
                    │   hos_engine.py     │
                    │                     │
                    │ • Driving limits    │
                    │ • Duty window       │
                    │ • Breaks & Rest     │
                    │ • Fuel stops        │
                    │ • Cycle tracking    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Generated Trip Plan │
                    │ + Daily HOS Schedule│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ React Visualization │
                    │ • Leaflet Map       │
                    │ • SVG ELD Logs      │
                  └─────────────────────┘
```

## 🛠️ Tech Stack
DomainTechnologies UsedBackendPython, Django, Django REST Framework, GunicornFrontendReact, Vite, JavaScript, LeafletAPIsOpenStreetMap Nominatim (Geocoding), OSRM (Routing)DeploymentVercel (Frontend), Render (Backend)DatabaseNone required — The engine is stateless and computes dynamically per request
📁 Project Structure
```
PlaintextHaulwise/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── eld_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── trip/
│       ├── hos_engine.py
│       ├── services.py
│       ├── views.py
│       └── urls.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── components/
│       │   ├── TripForm.jsx
│       │   ├── RouteMap.jsx
│       │   └── DailyLogSheet.jsx
│       └── App.jsx
│
├── screenshots/
│   ├── haulwise-map.png
│   └── haulwise-eld-log.png
│
└── README.md
```
## 🔄 Application Flow

```
PlaintextUser Inputs (Location, Pickup, Dropoff, Cycle Hours)
   │
   ▼
Geocoding (Nominatim) ──► Route Calculation (OSRM)
   │
   ▼
HOS Simulation (hos_engine.py)
   ├── Driving limit (11h) & Duty window (14h)
   ├── Mandatory breaks (30m) & Rest periods (10h)
   └── Fuel stops (~1000 mi) & Cycle limit (70h/8d)
   │
   ▼
Daily Schedule Generation (Day 1, Day 2, ...)
   │
   ▼
Frontend Visualization (Leaflet Map + SVG ELD Logs)
```
## 🚀 Run Locally

Prerequisites
Python 3
.xNode.js & npm
Git
Backend Setup
Clone the repository:
```
Bashgit clone [https://github.com/Shibam802/Haulwise.git](https://github.com/Shibam802/Haulwise.git)
cd Haulwise/backend
```
Create and activate a virtual environment:
Windows:
```
Bashpython -m venv venv
venv\Scripts\activate
```
macOS / Linux:
```
Bashpython3 -m venv venv
source venv/bin/activate
```
Install dependencies:
```
Bashpip install -r requirements.txt
```
Start the Django server:
```
Bashpython manage.py runserver
```
The backend will run at http://127.0.0.1:8000.Frontend SetupOpen a new terminal and navigate to the frontend directory:Bashcd Haulwise/frontend
Install dependencies:
```
Bashnpm install
Create a .env file inside frontend/:Code snippetVITE_API_BASE_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
```
Start the development server:
```
Bashnpm run dev
```
The frontend will run at http://localhost:5173.

## 🌐 API Reference
Plan TripPOST /api/plan-trip/
```
Request Body Example:JSON{
  "current_location": "Chicago, IL",
  "pickup_location": "Dallas, TX",
  "dropoff_location": "Houston, TX",
  "current_cycle_used": 20
}
```
## ☁️ Deployment Guide
Backend (Render)
Root Directory: backend
Build Command: pip install -r requirements.txtStart 
Command: gunicorn eld_backend.wsgi --log-file -Environment 
Variables:SECRET_KEY: your-secret-key
DEBUG: FalseALLOWED_HOSTS: https://haulwise-tawny.vercel.app
Root Directory: 
frontendEnvironment 
Variables:VITE_API_BASE_URL: https://haulwise-kg4g.onrender.com
## 📋 Assumptions & Legal Disclaimer
The simulation operates based on standard rules for a property-carrying driver operating on a 70-hour / 8-day cycle under standard conditions, assuming 1 hour each for pickup and drop-off, fuel stops every 1,000 miles, and zero adverse driving conditions.Disclaimer: Haulwise is an educational software engineering project designed to demonstrate constraint simulation and system design. It is not certified as an Electronic Logging Device (ELD) and should not be used as a substitute for official FMCSA regulatory compliance tools.
## 🎯 Features at a Glance📍 Geocoding: 
Real-time location parsing via Nominatim.
## 🗺️ Routing Engine: 
Distance and geometry calculation via OSRM.
## ⏱️ HOS Simulation: 
Dynamic constraint evaluation engine.
## ⛽ Fuel & Rest Planning: 
Automated stop insertion based on range and fatigue limits.
## 🔄 Cycle Tracking: 
Tracks total available cycle hours across multi-day trips.
## 📊 ELD Logs: 
Scalable Vector Graphics (SVG) daily grid visualizer.
##⚡ Stateless API: 
Zero database overhead; fully dynamic REST execution.
## 🔮 Future Enhancements[ ] 
Split sleeper-berth optimization option[ ] 
Team-driver schedule simulation[ ] 
Traffic and weather-aware ETA adjustments[ ] 
Alternative routing preferences (avoiding tolls, eco-routing)[ ] 
PDF export for daily ELD log sheets[ ] 
Comprehensive PyTest suite for hos_engine.py edge cases
## 📄 License
This project is open source and available under the MIT License.
