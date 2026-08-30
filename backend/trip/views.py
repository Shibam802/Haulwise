from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status

from . import services
from .hos_engine import plan_trip_schedule


class TripPlanView(APIView):
    """
    POST /api/plan-trip/
    body: {
      "current_location": "Chicago, IL",
      "pickup_location": "Indianapolis, IN",
      "dropoff_location": "Nashville, TN",
      "current_cycle_used": 12.5
    }
    """

    def post(self, request):
        data = request.data
        required = ["current_location", "pickup_location", "dropoff_location", "current_cycle_used"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            return Response(
                {"error": f"Missing required field(s): {', '.join(missing)}"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        try:
            cycle_used = float(data["current_cycle_used"])
        except (TypeError, ValueError):
            return Response(
                {"error": "current_cycle_used must be a number of hours."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        if cycle_used < 0 or cycle_used > 70:
            return Response(
                {"error": "current_cycle_used must be between 0 and 70."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        try:
            cur_lat, cur_lon, cur_name = services.geocode(data["current_location"])
            pu_lat, pu_lon, pu_name = services.geocode(data["pickup_location"])
            do_lat, do_lon, do_name = services.geocode(data["dropoff_location"])
        except services.GeocodeError as e:
            return Response({"error": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "The geocoding service is unavailable right now. Please try again shortly."},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )

        try:
            leg1 = services.route([(cur_lat, cur_lon), (pu_lat, pu_lon)])
            leg2 = services.route([(pu_lat, pu_lon), (do_lat, do_lon)])
        except services.RoutingError as e:
            return Response({"error": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "The routing service is unavailable right now. Please try again shortly."},
                status=http_status.HTTP_502_BAD_GATEWAY,
            )

        daily_logs, events, summary = plan_trip_schedule(
            {"distance_miles": leg1["distance_miles"], "duration_hours": leg1["duration_hours"]},
            {"distance_miles": leg2["distance_miles"], "duration_hours": leg2["duration_hours"]},
            cycle_used,
        )

        # Place fuel/rest/restart markers along the combined route geometry.
        combined_geometry = leg1["geometry"] + leg2["geometry"]
        leg1_miles = leg1["distance_miles"]
        stops = [
            {"type": "start", "label": "Current location", "name": cur_name, "position": [cur_lat, cur_lon]},
            {"type": "pickup", "label": "Pickup", "name": pu_name, "position": [pu_lat, pu_lon]},
            {"type": "dropoff", "label": "Drop-off", "name": do_name, "position": [do_lat, do_lon]},
        ]
        for ev in events:
            miles = ev["miles"]
            if miles <= leg1_miles:
                point = services.interpolate_along_route(leg1["geometry"], miles)
            else:
                point = services.interpolate_along_route(leg2["geometry"], miles - leg1_miles)
            if point:
                stops.append({"type": ev["type"], "label": ev["label"], "position": point})

        response = {
            "route": {
                "geometry": combined_geometry,
                "distance_miles": round(leg1["distance_miles"] + leg2["distance_miles"], 1),
                "driving_duration_hours": round(leg1["duration_hours"] + leg2["duration_hours"], 2),
                "legs": [
                    {
                        "from": cur_name,
                        "to": pu_name,
                        "distance_miles": round(leg1["distance_miles"], 1),
                        "duration_hours": round(leg1["duration_hours"], 2),
                    },
                    {
                        "from": pu_name,
                        "to": do_name,
                        "distance_miles": round(leg2["distance_miles"], 1),
                        "duration_hours": round(leg2["duration_hours"], 2),
                    },
                ],
            },
            "stops": stops,
            "daily_logs": daily_logs,
            "summary": summary,
        }
        return Response(response)
