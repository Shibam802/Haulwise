export default function TripSummary({ route, summary }) {
  const items = [
    { label: "Total distance", value: `${summary.total_distance_miles.toLocaleString()} mi` },
    { label: "Driving time", value: `${route.driving_duration_hours.toFixed(1)} hrs` },
    { label: "Log sheets needed", value: `${summary.total_days} day${summary.total_days === 1 ? "" : "s"}` },
    { label: "Cycle used → end", value: `${summary.cycle_hours_used_at_start.toFixed(1)}h → ${summary.cycle_hours_used_at_end.toFixed(1)}h` },
  ];
  return (
    <div className="summary-strip">
      {items.map((item) => (
        <div className="summary-strip__item" key={item.label}>
          <span className="summary-strip__value mono">{item.value}</span>
          <span className="summary-strip__label">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
