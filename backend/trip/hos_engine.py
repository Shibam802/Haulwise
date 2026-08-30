"""
Hours-of-Service (HOS) simulation engine.

Implements a simplified version of the FMCSA property-carrying driver rules
(49 CFR 395) for the purposes of this assessment:

  - 11-hour driving limit per duty period
  - 14-hour on-duty window per duty period (elapsed time, not just driving)
  - 30-minute break required after 8 cumulative hours of driving
  - 10 consecutive hours off duty (or sleeper berth) resets the 11/14 hr clocks
  - 70-hour / 8-day cycle limit; a 34-hour off-duty period restarts the cycle
  - A fuel stop is scheduled at least once every 1,000 miles
  - 1 hour on-duty (not driving) is allocated for pickup and for drop-off

Assumptions (stated explicitly, matching the assessment brief):
  - Property-carrying driver, 70 hrs / 8 days, no adverse driving conditions
  - The trip is assumed to start at hour 0 (midnight) of Day 1
  - "Current location" is where the driver/tractor starts; the driver then
    drives to the pickup, loads (1 hr on-duty), drives to the drop-off, and
    unloads (1 hr on-duty)

The output is a list of "days", each a fresh 24-hour grid (matching a single
paper log sheet), containing duty-status segments plus running totals.
"""

DRIVE_LIMIT = 11.0
DUTY_WINDOW = 14.0
BREAK_AFTER_DRIVE_HOURS = 8.0
BREAK_DURATION = 0.5
DAILY_RESET_DURATION = 10.0
CYCLE_LIMIT = 70.0
RESTART_DURATION = 34.0
FUEL_INTERVAL_MILES = 1000.0
FUEL_STOP_DURATION = 0.5
PICKUP_DURATION = 1.0
DROPOFF_DURATION = 1.0

STATUS_OFF_DUTY = "OFF_DUTY"
STATUS_SLEEPER = "SLEEPER_BERTH"
STATUS_DRIVING = "DRIVING"
STATUS_ON_DUTY = "ON_DUTY_NOT_DRIVING"

EPS = 1e-6


class HOSEngine:
    def __init__(self, current_cycle_used_hours: float):
        self.day = 1
        self.clock = 0.0  # hours elapsed within the current day (0-24)
        self.drive_window_left = DRIVE_LIMIT
        self.duty_window_left = DUTY_WINDOW
        self.drive_since_break = 0.0
        self.miles_since_fuel = 0.0
        self.cycle_used = max(0.0, current_cycle_used_hours)
        self.cumulative_miles = 0.0
        self.days = {1: []}
        self.events = []  # notable events for the "stops" list on the map

    # -- low level -----------------------------------------------------
    def _add_segment(self, status, hours, label):
        remaining = hours
        while remaining > EPS:
            space_in_day = 24 - self.clock
            take = min(remaining, space_in_day)
            if take > EPS:
                self.days.setdefault(self.day, []).append(
                    {
                        "start": round(self.clock, 3),
                        "end": round(self.clock + take, 3),
                        "status": status,
                        "label": label,
                    }
                )
            self.clock += take
            remaining -= take
            if self.clock >= 24 - EPS:
                self.clock = 0.0
                self.day += 1
                self.days.setdefault(self.day, [])

    def _insert_daily_reset(self):
        self._add_segment(STATUS_SLEEPER, DAILY_RESET_DURATION, "Required 10-hour rest")
        self.drive_window_left = DRIVE_LIMIT
        self.duty_window_left = DUTY_WINDOW
        self.drive_since_break = 0.0
        self.events.append({"type": "rest", "label": "10-hour reset", "miles": self.cumulative_miles})

    def _insert_restart(self):
        self._add_segment(
            STATUS_OFF_DUTY, RESTART_DURATION, "34-hour restart (70-hr/8-day cycle limit reached)"
        )
        self.drive_window_left = DRIVE_LIMIT
        self.duty_window_left = DUTY_WINDOW
        self.drive_since_break = 0.0
        self.cycle_used = 0.0
        self.events.append({"type": "restart", "label": "34-hour restart", "miles": self.cumulative_miles})

    def _insert_break(self):
        self._add_segment(STATUS_OFF_DUTY, BREAK_DURATION, "30-minute break")
        self.drive_since_break = 0.0
        self.duty_window_left = max(0.0, self.duty_window_left - BREAK_DURATION)
        self.events.append({"type": "break", "label": "30-minute break", "miles": self.cumulative_miles})

    def _insert_fuel_stop(self):
        self._add_segment(STATUS_ON_DUTY, FUEL_STOP_DURATION, "Fuel stop")
        self.miles_since_fuel = 0.0
        self.duty_window_left = max(0.0, self.duty_window_left - FUEL_STOP_DURATION)
        self.cycle_used += FUEL_STOP_DURATION
        self.events.append({"type": "fuel", "label": "Fuel stop", "miles": self.cumulative_miles})

    def _ensure_capacity_for_onduty(self, hours):
        """Force whatever reset is needed before an on-duty (non-driving) block."""
        guard = 0
        while (
            self.duty_window_left < hours - EPS or (CYCLE_LIMIT - self.cycle_used) < hours - EPS
        ):
            if (CYCLE_LIMIT - self.cycle_used) < hours - EPS:
                self._insert_restart()
            else:
                self._insert_daily_reset()
            guard += 1
            if guard > 20:
                break  # safety valve; should never trigger in practice

    # -- public ----------------------------------------------------------
    def add_on_duty(self, hours, label):
        self._ensure_capacity_for_onduty(hours)
        self._add_segment(STATUS_ON_DUTY, hours, label)
        self.duty_window_left -= hours
        self.cycle_used += hours

    def add_drive(self, total_hours, total_miles, label):
        if total_hours <= EPS:
            return
        avg_speed = total_miles / total_hours if total_hours > 0 else 0.0
        remaining_hours = total_hours

        guard = 0
        while remaining_hours > EPS:
            guard += 1
            if guard > 500:
                break  # safety valve

            candidates = {
                "drive_limit": self.drive_window_left,
                "duty_limit": self.duty_window_left,
                "break_limit": BREAK_AFTER_DRIVE_HOURS - self.drive_since_break,
                "cycle_limit": CYCLE_LIMIT - self.cycle_used,
            }
            if avg_speed > EPS:
                miles_left_before_fuel = FUEL_INTERVAL_MILES - self.miles_since_fuel
                candidates["fuel_limit"] = max(miles_left_before_fuel / avg_speed, 0.0)

            chunk = min(remaining_hours, *candidates.values())
            chunk = max(chunk, 0.0)

            if chunk > EPS:
                self._add_segment(STATUS_DRIVING, chunk, label)
                miles_chunk = chunk * avg_speed
                self.drive_window_left -= chunk
                self.duty_window_left -= chunk
                self.drive_since_break += chunk
                self.miles_since_fuel += miles_chunk
                self.cycle_used += chunk
                self.cumulative_miles += miles_chunk
                remaining_hours -= chunk

            if remaining_hours <= EPS:
                break

            # Decide which constraint to resolve, most-restrictive-in-reality first.
            binding = {k: v for k, v in candidates.items() if v <= chunk + 1e-4}
            if "cycle_limit" in binding:
                self._insert_restart()
            elif "duty_limit" in binding or "drive_limit" in binding:
                self._insert_daily_reset()
            elif "fuel_limit" in binding:
                self._insert_fuel_stop()
            elif "break_limit" in binding:
                self._insert_break()
            else:
                # Shouldn't happen, but avoid an infinite loop.
                self._insert_break()

    # -- output ------------------------------------------------------------
    def build_daily_logs(self):
        logs = []
        for day_num in sorted(self.days.keys()):
            segments = self.days[day_num]
            if not segments:
                continue
            totals = {STATUS_OFF_DUTY: 0.0, STATUS_SLEEPER: 0.0, STATUS_DRIVING: 0.0, STATUS_ON_DUTY: 0.0}
            for seg in segments:
                totals[seg["status"]] += seg["end"] - seg["start"]
            logs.append(
                {
                    "day": day_num,
                    "segments": segments,
                    "totals": {
                        "off_duty": round(totals[STATUS_OFF_DUTY], 2),
                        "sleeper_berth": round(totals[STATUS_SLEEPER], 2),
                        "driving": round(totals[STATUS_DRIVING], 2),
                        "on_duty_not_driving": round(totals[STATUS_ON_DUTY], 2),
                    },
                }
            )
        return logs


def plan_trip_schedule(leg1, leg2, current_cycle_used_hours):
    """
    leg1, leg2: dicts with 'distance_miles', 'duration_hours' (current->pickup,
    pickup->dropoff respectively).
    Returns (daily_logs, events, summary).
    """
    engine = HOSEngine(current_cycle_used_hours)

    engine.add_drive(leg1["duration_hours"], leg1["distance_miles"], "En route to pickup")
    engine.add_on_duty(PICKUP_DURATION, "At pickup location (loading)")
    engine.add_drive(leg2["duration_hours"], leg2["distance_miles"], "En route to drop-off")
    engine.add_on_duty(DROPOFF_DURATION, "At drop-off location (unloading)")

    daily_logs = engine.build_daily_logs()
    summary = {
        "total_days": len(daily_logs),
        "total_driving_hours": round(sum(d["totals"]["driving"] for d in daily_logs), 2),
        "total_on_duty_hours": round(
            sum(d["totals"]["driving"] + d["totals"]["on_duty_not_driving"] for d in daily_logs), 2
        ),
        "cycle_hours_used_at_start": round(current_cycle_used_hours, 2),
        "cycle_hours_used_at_end": round(engine.cycle_used, 2),
        "total_distance_miles": round(leg1["distance_miles"] + leg2["distance_miles"], 1),
    }
    return daily_logs, engine.events, summary
