const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export async function fetchJson(path) {
  const r = await fetch(`${API_BASE}${path}`, { headers: { "Accept": "application/json" } });
  if (!r.ok) {
    const txt = await r.text();
    throw new Error(`${r.status} ${r.statusText}: ${txt}`);
  }
  return await r.json();
}

export function listDevices(tenant = "demo") {
  return fetchJson(`/v1/tenants/${encodeURIComponent(tenant)}/devices`);
}

export function latest(tenant, deviceId) {
  return fetchJson(`/v1/tenants/${encodeURIComponent(tenant)}/devices/${encodeURIComponent(deviceId)}/latest`);
}

export function series(tenant, deviceId, metric, { from_ts, to_ts, limit = 2000 } = {}) {
  const p = new URLSearchParams({ metric, limit: String(limit) });
  if (from_ts) p.set("from_ts", from_ts);
  if (to_ts) p.set("to_ts", to_ts);
  return fetchJson(`/v1/tenants/${encodeURIComponent(tenant)}/devices/${encodeURIComponent(deviceId)}/series?${p.toString()}`);
}
