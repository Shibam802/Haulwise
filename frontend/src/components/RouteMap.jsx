import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const STOP_STYLES = {
  start: { color: "#2f9e8f", radius: 8, label: "Start" },
  pickup: { color: "#f2a93b", radius: 8, label: "Pickup" },
  dropoff: { color: "#d8503b", radius: 8, label: "Drop-off" },
  fuel: { color: "#64737b", radius: 6, label: "Fuel" },
  break: { color: "#9aa5aa", radius: 5, label: "30-min break" },
  rest: { color: "#14242f", radius: 6, label: "10-hr rest" },
  restart: { color: "#d8503b", radius: 6, label: "34-hr restart" },
};

function boundsFromGeometry(geometry) {
  const lats = geometry.map((p) => p[0]);
  const lons = geometry.map((p) => p[1]);
  return [
    [Math.min(...lats), Math.min(...lons)],
    [Math.max(...lats), Math.max(...lons)],
  ];
}

export default function RouteMap({ route, stops }) {
  if (!route?.geometry?.length) return null;
  const bounds = boundsFromGeometry(route.geometry);

  return (
    <div className="map-card">
      <MapContainer bounds={bounds} boundsOptions={{ padding: [32, 32] }} scrollWheelZoom={true} className="map-card__map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={route.geometry} pathOptions={{ color: "#f2a93b", weight: 4, opacity: 0.9 }} />
        {stops.map((stop, i) => {
          const style = STOP_STYLES[stop.type] || STOP_STYLES.fuel;
          return (
            <CircleMarker
              key={i}
              center={stop.position}
              radius={style.radius}
              pathOptions={{ color: "#10202b", weight: 2, fillColor: style.color, fillOpacity: 1 }}
            >
              <Tooltip direction="top" offset={[0, -6]}>
                {stop.name ? `${style.label}: ${stop.name}` : style.label}
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
      <Legend />
    </div>
  );
}

function Legend() {
  const items = ["start", "pickup", "dropoff", "fuel", "break", "rest"];
  return (
    <div className="map-legend">
      {items.map((key) => (
        <span className="map-legend__item" key={key}>
          <span className="map-legend__dot" style={{ background: STOP_STYLES[key].color }} />
          {STOP_STYLES[key].label}
        </span>
      ))}
    </div>
  );
}
