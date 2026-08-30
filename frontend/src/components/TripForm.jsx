import { useState } from "react";

const DEFAULTS = {
  currentLocation: "",
  pickupLocation: "",
  dropoffLocation: "",
  currentCycleUsed: "",
};

export default function TripForm({ onSubmit, loading }) {
  const [values, setValues] = useState(DEFAULTS);
  const [touched, setTouched] = useState(false);

  const handleChange = (field) => (e) => {
    setValues((v) => ({ ...v, [field]: e.target.value }));
  };

  const cycleNum = Number(values.currentCycleUsed);
  const cycleValid =
    values.currentCycleUsed !== "" && !Number.isNaN(cycleNum) && cycleNum >= 0 && cycleNum <= 70;

  const isValid =
    values.currentLocation.trim() &&
    values.pickupLocation.trim() &&
    values.dropoffLocation.trim() &&
    cycleValid;

  const handleSubmit = (e) => {
    e.preventDefault();
    setTouched(true);
    if (!isValid || loading) return;
    onSubmit(values);
  };

  return (
    <form className="ticket" onSubmit={handleSubmit} noValidate>
      <div className="ticket__header">
        <span className="ticket__eyebrow">Dispatch ticket</span>
        <h2 className="ticket__title">Plan this trip</h2>
      </div>

      <div className="ticket__grid">
        <Field
          label="Current location"
          placeholder="e.g. Chicago, IL"
          value={values.currentLocation}
          onChange={handleChange("currentLocation")}
          error={touched && !values.currentLocation.trim() ? "Required" : null}
        />
        <Field
          label="Pickup location"
          placeholder="e.g. Indianapolis, IN"
          value={values.pickupLocation}
          onChange={handleChange("pickupLocation")}
          error={touched && !values.pickupLocation.trim() ? "Required" : null}
        />
        <Field
          label="Drop-off location"
          placeholder="e.g. Nashville, TN"
          value={values.dropoffLocation}
          onChange={handleChange("dropoffLocation")}
          error={touched && !values.dropoffLocation.trim() ? "Required" : null}
        />
        <Field
          label="Current cycle used (hrs)"
          placeholder="0–70"
          value={values.currentCycleUsed}
          onChange={handleChange("currentCycleUsed")}
          type="number"
          min="0"
          max="70"
          step="0.5"
          error={touched && !cycleValid ? "Enter 0–70 hours" : null}
          hint="Hours already on duty in the current 70-hr / 8-day cycle"
        />
      </div>

      <button className="ticket__submit" type="submit" disabled={loading}>
        {loading ? "Routing…" : "Plan trip"}
      </button>
    </form>
  );
}

function Field({ label, error, hint, ...inputProps }) {
  return (
    <label className="field">
      <span className="field__label">{label}</span>
      <input className="field__input" {...inputProps} />
      {error ? <span className="field__error">{error}</span> : hint ? <span className="field__hint">{hint}</span> : null}
    </label>
  );
}
