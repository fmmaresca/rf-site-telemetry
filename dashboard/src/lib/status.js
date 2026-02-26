export function ageSeconds(ts) {
  if (!ts) return null;
  const t = Date.parse(ts);
  if (Number.isNaN(t)) return null;
  return Math.max(0, Math.floor((Date.now() - t) / 1000));
}

export function deviceState(age) {
  if (age == null) return { label: "unknown", color: "#9e9e9e" };
  if (age <= 60) return { label: "online", color: "#2e7d32" };
  if (age <= 300) return { label: "stale", color: "#f9a825" };
  return { label: "offline", color: "#c62828" };
}

export function fmtAge(s) {
  if (s == null) return "—";
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}
