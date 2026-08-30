const ROWS = [
  { key: "off_duty", status: "OFF_DUTY", label: "Off duty" },
  { key: "sleeper_berth", status: "SLEEPER_BERTH", label: "Sleeper berth" },
  { key: "driving", status: "DRIVING", label: "Driving" },
  { key: "on_duty_not_driving", status: "ON_DUTY_NOT_DRIVING", label: "On duty (not driving)" },
];

const ROW_INDEX = Object.fromEntries(ROWS.map((r, i) => [r.status, i]));

const LABEL_W = 128;
const HOUR_W = 26;
const ROW_H = 30;
const TOP_H = 22;
const CHART_W = HOUR_W * 24;
const CHART_H = ROW_H * ROWS.length;
const SVG_W = LABEL_W + CHART_W + 8;
const SVG_H = TOP_H + CHART_H + 6;

function xForHour(h) {
  return LABEL_W + h * HOUR_W;
}
function yForRow(i) {
  return TOP_H + i * ROW_H + ROW_H / 2;
}

function hourLabel(h) {
  if (h === 0) return "Mid";
  if (h === 12) return "Noon";
  return h > 12 ? String(h - 12) : String(h);
}

export default function DailyLogSheet({ log }) {
  const segments = log.segments;

  // Build the stepped duty-status path.
  let d = "";
  segments.forEach((seg, i) => {
    const rowI = ROW_INDEX[seg.status];
    const x1 = xForHour(seg.start);
    const x2 = xForHour(seg.end);
    const y = yForRow(rowI);
    if (i === 0) {
      d += `M ${x1} ${y} `;
    } else {
      const prevRowI = ROW_INDEX[segments[i - 1].status];
      if (prevRowI !== rowI) {
        d += `L ${x1} ${y} `; // vertical connector to this row
      }
    }
    d += `L ${x2} ${y} `;
  });

  return (
    <div className="log-sheet">
      <svg viewBox={`0 0 ${SVG_W} ${SVG_H}`} className="log-sheet__svg" role="img" aria-label={`Daily log grid for day ${log.day}`}>
        {/* hour gridlines */}
        {Array.from({ length: 25 }, (_, h) => (
          <line
            key={h}
            x1={xForHour(h)}
            y1={TOP_H}
            x2={xForHour(h)}
            y2={TOP_H + CHART_H}
            stroke={h % 6 === 0 ? "#b9c2c6" : "#dde2e4"}
            strokeWidth={h % 6 === 0 ? 1.2 : 1}
          />
        ))}
        {/* hour labels */}
        {Array.from({ length: 25 }, (_, h) => (
          <text key={h} x={xForHour(h)} y={TOP_H - 7} textAnchor="middle" className="log-sheet__hour-label">
            {h % 3 === 0 ? hourLabel(h % 24) : ""}
          </text>
        ))}
        {/* row backgrounds + labels + lines */}
        {ROWS.map((row, i) => (
          <g key={row.key}>
            <rect
              x={LABEL_W}
              y={TOP_H + i * ROW_H}
              width={CHART_W}
              height={ROW_H}
              fill={i % 2 === 0 ? "#fbfaf7" : "#f5f3ee"}
            />
            <line
              x1={LABEL_W}
              y1={TOP_H + i * ROW_H + ROW_H}
              x2={LABEL_W + CHART_W}
              y2={TOP_H + i * ROW_H + ROW_H}
              stroke="#b9c2c6"
              strokeWidth={1}
            />
            <text x={LABEL_W - 10} y={yForRow(i) + 4} textAnchor="end" className="log-sheet__row-label">
              {row.label}
            </text>
          </g>
        ))}
        <rect x={LABEL_W} y={TOP_H} width={CHART_W} height={CHART_H} fill="none" stroke="#10202b" strokeWidth={1.4} />
        {/* the duty-status trace itself */}
        <path d={d} fill="none" stroke="#10202b" strokeWidth={2.5} strokeLinejoin="round" />
        {segments.map((seg, i) => (
          <circle key={i} cx={xForHour(seg.start)} cy={yForRow(ROW_INDEX[seg.status])} r={2.6} fill="#f2a93b" />
        ))}
      </svg>

      <div className="log-sheet__totals">
        {ROWS.map((row) => (
          <span key={row.key} className="log-sheet__total">
            <strong className="mono">{log.totals[row.key].toFixed(1)}h</strong> {row.label}
          </span>
        ))}
      </div>

      <ol className="log-sheet__remarks">
        {segments.map((seg, i) => (
          <li key={i}>
            <span className="mono">{formatClock(seg.start)}–{formatClock(seg.end)}</span> — {seg.label}
          </li>
        ))}
      </ol>
    </div>
  );
}

function formatClock(hourFloat) {
  const totalMinutes = Math.round(hourFloat * 60);
  const h = Math.floor(totalMinutes / 60) % 24;
  const m = totalMinutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}
