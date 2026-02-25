import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { listDevices } from "../api.js";

function ageSeconds(ts) {
  if (!ts) return null;
  const t = Date.parse(ts);
  if (Number.isNaN(t)) return null;
  return Math.max(0, Math.floor((Date.now() - t) / 1000));
}

function fmtAge(s) {
  if (s == null) return "—";
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h`;
  const d = Math.floor(h / 24);
  return `${d}d`;
}

export default function Devices() {
  const tenant = "demo";
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const data = await listDevices(tenant);
        if (alive) setRows(data);
      } catch (e) {
        if (alive) setErr(String(e));
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  const table = useMemo(() => {
    return rows.map(r => ({
      ...r,
      age_s: ageSeconds(r.last_seen_at),
    })).sort((a, b) => (a.device_id > b.device_id ? 1 : -1));
  }, [rows]);

  if (err) {
    return <pre style={{ color: "crimson", whiteSpace: "pre-wrap" }}>{err}</pre>;
  }

  return (
    <div>
      <h2 style={{ margin: "8px 0 12px", fontSize: 18 }}>Devices</h2>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
              <th style={{ padding: 8 }}>Device</th>
              <th style={{ padding: 8 }}>Last seen</th>
              <th style={{ padding: 8 }}>Age</th>
            </tr>
          </thead>
          <tbody>
            {table.map(r => (
              <tr key={r.device_id} style={{ borderBottom: "1px solid #f0f0f0" }}>
                <td style={{ padding: 8 }}>
                  <Link to={`/device/${encodeURIComponent(r.device_id)}`}>{r.device_id}</Link>
                </td>
                <td style={{ padding: 8, fontFamily: "ui-monospace, monospace" }}>
                  {r.last_seen_at ?? "—"}
                </td>
                <td style={{ padding: 8 }}>{fmtAge(r.age_s)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


import React, { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Chart } from "chart.js/auto";
import { latest, series } from "../api.js";

function isoFromNow(hours) {
  const t = new Date(Date.now() - hours * 3600 * 1000);
  return t.toISOString();
}

function useChart(canvasRef, label) {
  const chartRef = useRef(null);

  function setData(points) {
    const labels = points.map(p => new Date(p.ts).toLocaleString());
    const values = points.map(p => p.value);

    if (!chartRef.current) {
      chartRef.current = new Chart(canvasRef.current, {
        type: "line",
        data: {
          labels,
          datasets: [{ label, data: values, tension: 0.15, pointRadius: 0 }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { maxTicksLimit: 8 } }
          }
        }
      });
    } else {
      chartRef.current.data.labels = labels;
      chartRef.current.data.datasets[0].data = values;
      chartRef.current.update();
    }
  }

  function destroy() {
    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }
  }

  return { setData, destroy };
}

export default function Device() {
  const tenant = "demo";
  const { deviceId } = useParams();

  const [rangeH, setRangeH] = useState(24);
  const [lat, setLat] = useState(null);
  const [err, setErr] = useState(null);

  const tempCanvas = useRef(null);
  const v12Canvas = useRef(null);

  const tempChart = useMemo(() => useChart(tempCanvas, "temp_c"), []);
  const v12Chart = useMemo(() => useChart(v12Canvas, "psu_12v / psu_5v"), []);

  useEffect(() => {
    return () => { tempChart.destroy(); v12Chart.destroy(); };
  }, []);

  async function loadAll() {
    try {
      setErr(null);
      const l = await latest(tenant, deviceId);
      setLat(l);

      const from_ts = isoFromNow(rangeH);

      const t = await series(tenant, deviceId, "temp_c", { from_ts, limit: 2000 });
      tempChart.setData(t);

      const s12 = await series(tenant, deviceId, "psu_12v", { from_ts, limit: 2000 });
      // for second chart we combine 12v + 5v into one dataset by plotting 12v only for now (MVP)
      // keep it simple: show 12v; (we can add multi-dataset next)
      v12Chart.setData(s12);
    } catch (e) {
      setErr(String(e));
    }
  }

  useEffect(() => {
    let alive = true;
    (async () => { if (alive) await loadAll(); })();
    const t = setInterval(() => { if (alive) loadAll(); }, 5000);
    return () => { alive = false; clearInterval(t); };
  }, [deviceId, rangeH]);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
        <h2 style={{ margin: "8px 0 12px", fontSize: 18 }}>Device: {deviceId}</h2>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span style={{ opacity: 0.7, fontSize: 13 }}>Range</span>
          {[1, 6, 24, 168].map(h => (
            <button
              key={h}
              onClick={() => setRangeH(h)}
              style={{
                padding: "6px 10px",
                borderRadius: 8,
                border: "1px solid #ddd",
                background: rangeH === h ? "#f0f0f0" : "white",
                cursor: "pointer"
              }}
            >
              {h === 168 ? "7d" : `${h}h`}
            </button>
          ))}
        </div>
      </div>

      {err && <pre style={{ color: "crimson", whiteSpace: "pre-wrap" }}>{err}</pre>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>temp_c</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.temp_c ?? "—"}</div>
        </div>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>psu_12v</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.psu_12v ?? "—"}</div>
        </div>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>psu_5v</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.psu_5v ?? "—"}</div>
        </div>
      </div>

      <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ marginBottom: 8, fontWeight: 600 }}>Temperature</div>
          <div style={{ height: 280 }}>
            <canvas ref={tempCanvas}></canvas>
          </div>
        </div>

        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ marginBottom: 8, fontWeight: 600 }}>PSU 12V</div>
          <div style={{ height: 280 }}>
            <canvas ref={v12Canvas}></canvas>
          </div>
          <div style={{ opacity: 0.7, fontSize: 12, marginTop: 6 }}>
            (MVP: showing 12V series; we can add 5V as a second dataset next.)
          </div>
        </div>
      </div>
    </div>
  );
}
