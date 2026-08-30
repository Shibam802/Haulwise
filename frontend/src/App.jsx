import { useState } from "react";
import TripForm from "./components/TripForm";
import RouteMap from "./components/RouteMap";
import TripSummary from "./components/TripSummary";
import DailyLogSheet from "./components/DailyLogSheet";
import { planTrip } from "./api";
import "./tokens.css";
import "./app.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeDay, setActiveDay] = useState(0);

  const handleSubmit = async (values) => {
    setLoading(true);
    setError(null);
    try {
      const data = await planTrip({
        currentLocation: values.currentLocation,
        pickupLocation: values.pickupLocation,
        dropoffLocation: values.dropoffLocation,
        currentCycleUsed: Number(values.currentCycleUsed),
      });
      setResult(data);
      setActiveDay(0);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__brand">
          <span className="app__brand-mark">●●●</span>
          <span className="app__brand-name">Haulwise</span>
        </div>
        <p className="app__tagline">Route planning &amp; FMCSA-style daily driver logs, from three stops and a cycle number.</p>
      </header>

      <main className="app__main">
        <TripForm onSubmit={handleSubmit} loading={loading} />

        {error && (
          <div className="alert-banner" role="alert">
            {error}
          </div>
        )}

        {loading && (
          <div className="loading-banner" aria-live="polite">
            Geocoding stops, routing the trip, and building your log sheets…
          </div>
        )}

        {result && !loading && (
          <section className="results">
            <TripSummary route={result.route} summary={result.summary} />

            <div className="results__grid">
              <RouteMap route={result.route} stops={result.stops} />
              <LegSummary legs={result.route.legs} />
            </div>

            <div className="log-section">
              <h2 className="log-section__title">Daily log sheets</h2>
              <div className="day-tabs" role="tablist" aria-label="Select day">
                {result.daily_logs.map((log, i) => (
                  <button
                    key={log.day}
                    role="tab"
                    aria-selected={activeDay === i}
                    className={`day-tabs__tab ${activeDay === i ? "day-tabs__tab--active" : ""}`}
                    onClick={() => setActiveDay(i)}
                  >
                    Day {log.day}
                  </button>
                ))}
              </div>
              <DailyLogSheet log={result.daily_logs[activeDay]} />
            </div>
          </section>
        )}

        {!result && !loading && !error && (
          <p className="empty-hint">
            Enter a start point, pickup, drop-off, and how many hours you've already used in your 70-hour/8-day
            cycle. Assumes a property-carrying driver, no adverse conditions, and a fuel stop every 1,000 miles.
          </p>
        )}
      </main>

      <footer className="app__footer">
        Routing via OSRM · Geocoding via OpenStreetMap Nominatim · Not a substitute for an FMCSA-certified ELD.
      </footer>
    </div>
  );
}

function LegSummary({ legs }) {
  return (
    <div className="leg-summary">
      <h3 className="leg-summary__title">Route legs</h3>
      <ol className="leg-summary__list">
        {legs.map((leg, i) => (
          <li key={i}>
            <div className="leg-summary__route">
              {leg.from} → {leg.to}
            </div>
            <div className="leg-summary__meta mono">
              {leg.distance_miles.toLocaleString()} mi · {leg.duration_hours.toFixed(1)} hrs
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
