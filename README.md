# 🚛 Haulwise — Trip & ELD Log Planner

A full-stack **Trip Planner and Electronic Logging Device (ELD) Log Simulator** for property-carrying truck drivers.

Haulwise takes the driver's current location, pickup location, drop-off location, and hours already used in the current **70-hour / 8-day cycle** and generates an HOS-compliant trip plan.

## ✨ Features

* 📍 Geocodes current, pickup, and drop-off locations
* 🗺️ Calculates driving routes using OSRM
* ⏱️ Simulates FMCSA Hours-of-Service (HOS) rules
* 🚚 Enforces the 11-hour driving limit
* ⏰ Enforces the 14-hour duty window
* 🛑 Automatically schedules the required 30-minute break
* 💤 Handles 10-hour daily rest periods
* 🔄 Handles the 70-hour / 8-day cycle
* 🔁 Supports the 34-hour restart
* ⛽ Automatically schedules fuel stops every 1,000 miles
* 📦 Includes 1-hour pickup and drop-off activities
* 🗺️ Displays routes and stops on an interactive map
* 🧾 Generates FMCSA-style daily ELD log sheets
* ⚛️ React + Vite frontend
* 🐍 Django REST API backend
* 🚀 Ready for deployment with Render and Vercel

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* Leaflet
* JavaScript
* HTML / CSS

### Backend

* Python
* Django
* Django REST Framework
* Gunicorn

### External Services

* **OpenStreetMap Nominatim** — Geocoding
* **OSRM** — Driving routes, distance, and duration

### Database

No database is required.

The backend API is stateless and processes each trip request independently.

---

## 📁 Project Structure

```text
eld-app/
│
├── backend/
│   ├── eld_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── ...
│   │
│   ├── trip/
│   │   ├── hos_engine.py
│   │   ├── services.py
│   │   ├── views.py
│   │   └── ...
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── Procfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TripForm/
│   │   │   ├── RouteMap/
│   │   │   └── DailyLogSheet/
│   │   ├── App.jsx
│   │   └── ...
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have the following installed:

* Python 3.10+
* Node.js 18+
* npm
* Git

---

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd eld-app
```

---

# 🐍 Backend Setup

Navigate to the backend:

```bash
cd backend
```

### Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the Django server

```bash
python manage.py runserver
```

The backend will run at:

```text
http://127.0.0.1:8000
```

No database configuration is required.

---

# ⚛️ Frontend Setup

Open another terminal and navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

# 🔗 Environment Configuration

The frontend communicates with the Django backend through:

```env
VITE_API_BASE_URL
```

Create a `.env` file inside the `frontend` directory.

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

For deployment, replace the local URL with the deployed backend URL.

Example:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

> ⚠️ Do not commit `.env` files containing secrets to GitHub.

---

# 🧠 FMCSA HOS Simulation

Haulwise implements the HOS constraints specified in the assessment requirements.

## 🚚 11-Hour Driving Limit

The driver can drive for a maximum of:

```text
11 hours
```

within a qualifying duty period.

---

## ⏰ 14-Hour Duty Window

The driver operates within a:

```text
14-hour duty window
```

Once the window expires, additional driving is not allowed until the required reset.

---

## 🛑 30-Minute Break

A 30-minute break is scheduled after:

```text
8 hours of cumulative driving
```

---

## 💤 10-Hour Reset

A qualifying:

```text
10-hour off-duty rest
```

resets the driver's daily driving and duty-window constraints.

---

## 🔄 70-Hour / 8-Day Cycle

The system tracks the driver's available hours within the:

```text
70 hours / 8 days
```

cycle.

---

## 🔁 34-Hour Restart

When the cycle limit is reached, the planner schedules:

```text
34-hour restart
```

to reset the cycle.

---

## ⛽ Fuel Stops

Fuel stops are automatically scheduled at least every:

```text
1,000 miles
```

Each fuel stop requires:

```text
30 minutes
```

of on-duty time.

---

## 📦 Pickup & Drop-off

The planner allocates:

```text
Pickup:    1 hour on-duty
Drop-off:  1 hour on-duty
```

---

# 🗺️ Route Planning

Haulwise uses **Nominatim** to convert location names into coordinates.

```text
Location Name
      ↓
   Nominatim
      ↓
Latitude + Longitude
```

The coordinates are then sent to **OSRM** to calculate the driving route.

```text
Current Location
       ↓
      OSRM
       ↓
Driving Route
       ↓
Distance + Duration
       ↓
HOS Engine
       ↓
Trip Plan
```

The resulting route and scheduled stops are displayed using **Leaflet**.

---

# 🧾 ELD Daily Log Sheets

Haulwise generates FMCSA-style daily log sheets using SVG.

Each log contains a:

```text
24-hour timeline
```

representing the driver's duty status throughout the day.

The log can display:

* 🟢 Off Duty
* 🔵 Sleeper Berth / Rest
* 🟠 Driving
* 🟣 On Duty
* ⛽ Fuel Stops
* 📦 Pickup
* 📦 Drop-off
* 🛑 Required Breaks

For longer trips, users can switch between different daily log sheets.

---

# 📋 Assumptions

The implementation follows the assumptions provided in the assessment brief.

### Driver

* Property-carrying driver
* 70-hour / 8-day cycle
* No adverse driving conditions

### Trip Start

The trip begins at:

```text
Hour 0 (midnight) — Day 1
```

### Pickup

```text
1 hour on-duty
```

### Drop-off

```text
1 hour on-duty
```

### Fuel

A 30-minute on-duty fuel stop is scheduled at least every 1,000 miles.

### Daily Log

Each daily log represents a fresh 24-hour period beginning when the driver returns to duty after a qualifying 10-hour rest or 34-hour restart.

This approach allows rest periods crossing calendar midnight to be represented correctly within the generated log period.

---

# 🌐 Third-Party Services

| Service       | Purpose                    |
| ------------- | -------------------------- |
| OpenStreetMap | Map data                   |
| Nominatim     | Geocoding                  |
| OSRM          | Driving route and distance |
| Leaflet       | Interactive map            |

These services are used without API keys for the assessment implementation.

> **Production Note:** Public demo services have usage and rate limits. A production deployment should use a managed provider or self-hosted routing/geocoding infrastructure.

---

# ☁️ Deployment

## Backend — Render

1. Push the repository to GitHub.
2. Create a new **Web Service** on Render.
3. Connect the GitHub repository.
4. Set the root directory to:

```text
backend
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn eld_backend.wsgi --log-file -
```

### Environment Variables

Configure:

```text
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-render-domain>
CORS_EXTRA_ORIGINS=<your-vercel-url>
```

Example:

```text
CORS_EXTRA_ORIGINS=https://your-app.vercel.app
```

After deployment, you will receive a backend URL such as:

```text
https://haulwise-api.onrender.com
```

---

# ▲ Frontend — Vercel

1. Create a new Vercel project.
2. Import the same GitHub repository.
3. Set the root directory to:

```text
frontend
```

4. Vercel should automatically detect **Vite**.

Add the environment variable:

```text
VITE_API_BASE_URL=https://haulwise-api.onrender.com
```

Deploy the application.

Your frontend will receive a URL similar to:

```text
https://haulwise.vercel.app
```

Add the Vercel URL to the backend CORS configuration if required.

---

# 🎥 Loom Walkthrough

For the project demonstration, the following flow is recommended:

### 1. Dispatch Form

Show the trip form and enter:

* Current location
* Pickup location
* Drop-off location
* Hours already used in the current cycle

Submit the trip.

### 2. Route & Summary

Demonstrate:

* Calculated route
* Total distance
* Estimated driving time
* Pickup
* Drop-off
* Rest periods
* Fuel stops
* Breaks

### 3. Daily Log Sheets

For a multi-day trip, switch between the daily log tabs.

Point out:

* Driving periods
* On-duty periods
* Off-duty periods
* 30-minute break
* 10-hour rest
* Fuel stop
* 34-hour restart when applicable

### 4. HOS Engine

Open:

```text
backend/trip/hos_engine.py
```

The key function to explain is:

```text
add_drive()
```

This is where the main HOS constraint logic is implemented, including:

* Driving limits
* Duty-window limits
* Break requirements
* Fuel intervals
* Cycle-hour limits
* 10-hour resets
* 34-hour restart logic

### 5. Explain the Assumptions

Mention the assessment assumptions explicitly:

```text
11-hour driving limit
14-hour duty window
30-minute break after 8 hours
10-hour reset
70-hour / 8-day cycle
34-hour restart
1,000-mile fuel interval
1-hour pickup
1-hour drop-off
```

---

# 🔐 Git & Security

The following files and directories should **not** be committed:

```text
.venv/
venv/
.env
node_modules/
__pycache__/
*.pyc
```

Use a `.gitignore` file such as:

```gitignore
# Python
.venv/
venv/
__pycache__/
*.py[cod]

# Environment variables
.env
.env.*
!.env.example

# Node
node_modules/
dist/
build/

# Django
*.log
db.sqlite3

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

The Python virtual environment should **never be uploaded** to GitHub.

Instead, dependencies are stored in:

```text
backend/requirements.txt
```

Anyone cloning the project can recreate the environment using:

```bash
python -m venv .venv
pip install -r backend/requirements.txt
```

---

# 📊 Application Flow

```text
                    ┌──────────────────┐
                    │   Trip Form      │
                    │ Current Location │
                    │ Pickup           │
                    │ Drop-off         │
                    │ Cycle Hours      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Nominatim     │
                    │    Geocoding     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      OSRM        │
                    │ Route + Distance │
                    │ + Duration       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    HOS Engine    │
                    │                  │
                    │ 11h Driving      │
                    │ 14h Duty         │
                    │ 30m Break        │
                    │ 10h Reset        │
                    │ 70/8 Cycle      │
                    │ 34h Restart      │
                    │ Fuel Stops       │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │   Route Map     │       │   Daily ELD     │
       │                 │       │   Log Sheets    │
       │ Route + Stops   │       │ 24-hour grids   │
       └─────────────────┘       └─────────────────┘
```

---

# 🎯 Project Objective

The objective of Haulwise is to demonstrate how a full-stack application can combine:

* Geographic routing
* Constraint-based scheduling
* FMCSA HOS rules
* Interactive mapping
* ELD-style visualization
* REST API architecture

to produce a practical trip-planning solution for commercial truck drivers.

---

## 👨‍💻 Project

**Haulwise — Trip & ELD Log Planner**

**Backend:** Django + Django REST Framework
**Frontend:** React + Vite
**Mapping:** Leaflet + OpenStreetMap
**Routing:** OSRM
**Geocoding:** Nominatim


 
 
